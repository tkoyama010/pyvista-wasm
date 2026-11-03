import fs from "node:fs";
import os from "node:os";
import process from "node:process";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
// "typebox" is one of pi's built-in extension imports (see pi docs,
// "Available Imports"), and it is also declared in package.json so that
// module resolution works in clean checkouts.
import { Type } from "typebox";

// Transifex API v3 extension: lets the agent list untranslated strings and
// save translations via the public REST API. Requires TX_TOKEN (Bearer token
// from https://app.transifex.com/user/settings/) or a token stored in
// ~/.tx-token as a fallback.
//
// Preconfigured for the pyvista-wasm project: the org and project parameters
// default to tkoyama010/pyvista-wasm-doc (https://app.transifex.com/tkoyama010/pyvista-wasm-doc/)
// and can be overridden when calling the tools.

const API = "https://rest.api.transifex.com";
const DEFAULT_ORG = "tkoyama010";
const DEFAULT_PROJECT = "pyvista-wasm-doc";

type JsonApiItem = {
	id: string;
	attributes: Record<string, unknown>;
	relationships?: Record<string, { data?: { id: string } }>;
};

type JsonApiResponse = {
	data: JsonApiItem[];
	included?: JsonApiItem[];
	links?: { next?: string | null };
};

function token(): string {
	let value = process.env.TX_TOKEN;
	if (!value) {
		// Fallback: read token from a file in the user's home directory so a
		// full pi restart is not required. os.homedir() is safe even when HOME
		// is unset.
		const tokenFile = `${os.homedir()}/.tx-token`;
		if (fs.existsSync(tokenFile)) {
			value = fs.readFileSync(tokenFile, "utf8").trim();
		}
	}
	if (!value) {
		throw new Error(
			"TX_TOKEN is not set. Generate an API token at https://app.transifex.com/user/settings/ and either export TX_TOKEN or store the token in ~/.tx-token.",
		);
	}
	return value;
}

async function txGet(path: string): Promise<JsonApiResponse> {
	const response = await fetch(
		path.startsWith("http") ? path : `${API}${path}`,
		{
			headers: {
				Accept: "application/vnd.api+json",
				Authorization: `Bearer ${token()}`,
			},
		},
	);
	if (!response.ok) {
		throw new Error(
			`Transifex API ${response.status}: ${await response.text()}`,
		);
	}
	return (await response.json()) as JsonApiResponse;
}

function resourceId(org: string, project: string, resource: string): string {
	return `o:${org}:p:${project}:r:${resource}`;
}

/** Narrow the unknown `strings` attribute into a plural-form map. */
function stringsOf(item: JsonApiItem): Record<string, string> {
	return (item.attributes.strings as Record<string, string> | undefined) ?? {};
}

/** Only follow pagination links on the Transifex API origin, so the bearer token is never sent to another host. */
function nextPath(next: string | undefined | null): string | undefined {
	if (!next) return undefined;
	const url = next.startsWith("http") ? next : `${API}${next}`;
	return url.startsWith(`${API}/`) ? url : undefined;
}

/**
 * RST inline literal closing markers (``) must not be immediately followed
 * by a CJK fullwidth opening bracket. Sphinx gettext substitutes the
 * translation back into the RST source verbatim, and docutils only accepts
 * an inline-literal ENDING marker when the character AFTER it is not suited
 * for the next inline start. A fullwidth `（` directly after a closing ```
 * desynchronizes the backtick matching and the rest of the paragraph renders
 * as visible raw backticks (reproduced locally with docutils 0.23; adding a
 * space before the bracket fixes it).
 */
export function looksSafeForRstRendering(text: string): boolean {
	return !/`{2,}(?=[（「『【〔])/.test(text);
}

/** Return the (slot id, key, source) triples of untranslated strings from a resource_translations response. */
export function pickUntranslated(
	response: JsonApiResponse,
): Array<{ id: string; key: string; source: string }> {
	const includedById = new Map<string, JsonApiItem>(
		(response.included ?? []).map((item) => [item.id, item]),
	);
	const result: Array<{ id: string; key: string; source: string }> = [];
	for (const item of response.data) {
		// Untranslated slots have strings null or all forms empty. Any populated
		// plural form counts as translated.
		const forms = stringsOf(item);
		if (Object.values(forms).some(Boolean)) continue;
		const resourceString = includedById.get(
			item.relationships?.resource_string?.data?.id ?? "",
		);
		if (!resourceString) continue;
		result.push({
			id: item.id,
			key: String(resourceString.attributes.key ?? ""),
			source: String(stringsOf(resourceString).other ?? ""),
		});
	}
	return result;
}

export default function (pi: ExtensionAPI) {
	pi.registerTool({
		name: "transifex_list_resources",
		label: "Transifex: List Resources",
		description:
			"List resources (slug, name, categories) in a Transifex project. Uses TX_TOKEN env var or ~/.tx-token file.",
		parameters: Type.Object({
			org: Type.Optional(
				Type.String({ description: `Organization slug (default: ${DEFAULT_ORG})` }),
			),
			project: Type.Optional(
				Type.String({ description: `Project slug (default: ${DEFAULT_PROJECT})` }),
			),
		}),
		async execute(_toolCallId, params) {
			const org = params.org ?? DEFAULT_ORG;
			const project = params.project ?? DEFAULT_PROJECT;
			const query = new URLSearchParams({
				"filter[project]": `o:${org}:p:${project}`,
			});
			const resources: JsonApiItem[] = [];
			let path: string | undefined = `/resources?${query}`;
			while (path) {
				const json = await txGet(path);
				resources.push(...json.data);
				path = nextPath(json.links?.next);
			}
			const text = JSON.stringify(
				resources.map((r) => ({
					slug: r.attributes.slug,
					name: r.attributes.name,
					categories: r.attributes.categories,
				})),
				null,
				2,
			);
			return { content: [{ type: "text", text }], details: {} };
		},
	});

	pi.registerTool({
		name: "transifex_get_untranslated",
		label: "Transifex: Get Untranslated",
		description:
			"Fetch untranslated strings (slot id, key, source text) for one resource and language. Translate them with transifex_translate.",
		parameters: Type.Object({
			org: Type.Optional(
				Type.String({ description: `Organization slug (default: ${DEFAULT_ORG})` }),
			),
			project: Type.Optional(
				Type.String({ description: `Project slug (default: ${DEFAULT_PROJECT})` }),
			),
			resource: Type.String({ description: "Resource slug" }),
			lang: Type.String({ description: "Target language code, e.g. ja" }),
			limit: Type.Optional(
				Type.Number({ description: "Max strings to return (default 50)" }),
			),
		}),
		async execute(_toolCallId, params) {
			// Normalize: reject negative/fractional values so slice(0, limit)
			// cannot violate the stated maximum.
			const limit = Math.max(1, Math.floor(params.limit ?? 50));
			const query = new URLSearchParams({
				"filter[resource]": resourceId(
					params.org ?? DEFAULT_ORG,
					params.project ?? DEFAULT_PROJECT,
					params.resource,
				),
				"filter[language]": `l:${params.lang}`,
				include: "resource_string",
				// resource_translations rejects page[limit]/page[number]; it uses
				// cursor pagination, which the links.next loop below follows.
			});
			const untranslated: Array<{ id: string; key: string; source: string }> =
				[];
			let path: string | undefined = `/resource_translations?${query}`;
			while (path && untranslated.length < limit) {
				const json = await txGet(path);
				untranslated.push(...pickUntranslated(json));
				path = nextPath(json.links?.next);
			}
			const text = JSON.stringify(untranslated.slice(0, limit), null, 2);
			return { content: [{ type: "text", text }], details: {} };
		},
	});

	pi.registerTool({
		name: "transifex_translate",
		label: "Transifex: Save Translation",
		description:
			"Save translations for untranslated strings. Pass one entry per string: the slot id and translated text from transifex_get_untranslated. Omit text to copy the source string unchanged (for markup/identifier strings that must not be translated).",
		parameters: Type.Object({
			translations: Type.Array(
				Type.Object({
					id: Type.String({ description: "Resource translation slot id" }),
					text: Type.Optional(
						Type.String({
							description: "Translated text; omit to copy the source string",
						}),
					),
					form: Type.Optional(
						Type.String({
							description:
								'Plural form key to set when text is given (default: "other")',
						}),
					),
				}),
			),
		}),
		async execute(_toolCallId, params) {
			const saved: string[] = [];
			const failed: Array<{ id: string; error: string }> = [];
			for (const { id, text, form } of params.translations) {
				// Caller-controlled id goes into a URL path segment; validate it
				// against the official Transifex resource-translation id format
				// (o:org:p:project:r:resource:s:hash:l:language) so nothing that
				// could escape the endpoint is accepted.
				const TRANSLATION_ID_RE =
					/^o:[a-zA-Z0-9._-]+:p:[a-zA-Z0-9_-]+:r:[a-zA-Z0-9_-]+:s:[0-9a-fA-F]{32}:l:[a-zA-Z0-9@_-]+$/;
				if (!TRANSLATION_ID_RE.test(id)) {
					failed.push({ id, error: "invalid resource translation id" });
					continue;
				}
				let strings: Record<string, string>;
				let json: JsonApiResponse;
				try {
					// PATCH replaces the whole plural-form map, so fetch the current
					// slot first and merge into it (json.data is the target slot;
					// included holds the source resource_string).
					// ponytail: read-merge-PATCH has a small lost-update window; the
					// Transifex API v3 does not support ETag/If-Match conditional
					// updates, so conflicts cannot be rejected server-side. Retry
					// failed-looking saves if another translator edited the slot
					// concurrently.
					json = await txGet(
						`/resource_translations/${id}?include=resource_string`,
					);
					const slot = Array.isArray(json.data) ? json.data[0] : json.data;
					strings = stringsOf(slot ?? ({} as JsonApiItem));
				} catch (error) {
					failed.push({ id, error: String(error) });
					continue;
				}
				if (text === undefined) {
					// Copy source: take every plural form from the source string.
					const source = stringsOf(
						(json.included?.[0] ?? ({} as JsonApiItem)) as JsonApiItem,
					);
					// Fail closed: never PATCH an empty source (it would wipe the
					// translation slot).
					if (!Object.values(source).some(Boolean)) {
						failed.push({
							id,
							error: "source string is missing or empty; not overwritten",
						});
						continue;
					}
					Object.assign(strings, source);
				} else {
					// Fail closed: never PATCH an empty translation either; a blank
					// model result would erase the slot.
					if (!text) {
						failed.push({ id, error: "empty translation text; not saved" });
						continue;
					}
					// Fail closed on markup that breaks the Sphinx ja build: an
					// RST inline literal ending right before a fullwidth bracket
					// renders raw backticks on the site (e.g. ``'surface'``（デフォルト）).
					// Space before the bracket, or rephrase.
					if (!looksSafeForRstRendering(text)) {
						failed.push({
							id,
							error:
								'translation ends an RST inline literal (``) directly before a fullwidth bracket (（「『【〔); insert a space after the closing backticks or rephrase',
						});
						continue;
					}
					strings = { ...strings, [form ?? "other"]: text };
				}
				try {
					const response = await fetch(`${API}/resource_translations/${id}`, {
						method: "PATCH",
						headers: {
							"Content-Type": "application/vnd.api+json",
							Accept: "application/vnd.api+json",
							Authorization: `Bearer ${token()}`,
						},
						body: JSON.stringify({
							data: {
								id,
								type: "resource_translations",
								attributes: { strings },
							},
						}),
					});
					if (response.ok) {
						saved.push(id);
					} else {
						failed.push({
							id,
							error: `${response.status}: ${await response.text()}`,
						});
					}
				} catch (error) {
					// Network/auth failures must not reject the whole batch; keep
					// earlier partial results reportable.
					failed.push({ id, error: String(error) });
				}
			}
			const text = JSON.stringify({ saved, failed }, null, 2);
			return { content: [{ type: "text", text }], details: {} };
		},
	});
}
