// biome-ignore lint/correctness/noUndeclaredVariables: ESLint plugin import
import jsdocPlugin from "eslint-plugin-jsdoc";

// biome-ignore lint/style/noDefaultExport: ESLint config requires default export
export default [
  {
    space: true,
    prettier: true,
    semicolon: true,
    ignores: ["src/"],
    plugins: {
      jsdoc: jsdocPlugin,
    },
    rules: {
      // VTK.wasm bridges require assertions between its untyped API and our typed interfaces
      "@typescript-eslint/no-unsafe-type-assertion": "off",
      "jsdoc/require-jsdoc": [
        "error",
        {
          require: {
            // biome-ignore lint/style/useNamingConvention: ESLint plugin convention
            FunctionDeclaration: true,
            // biome-ignore lint/style/useNamingConvention: ESLint plugin convention
            MethodDefinition: true,
            // biome-ignore lint/style/useNamingConvention: ESLint plugin convention
            ClassDeclaration: true,
          },
          contexts: ["TSInterfaceDeclaration", "TSTypeAliasDeclaration"],
        },
      ],
      "jsdoc/require-description": "error",
      "jsdoc/no-blank-blocks": "error",
      "jsdoc/no-blank-block-descriptions": "error",
      "jsdoc/require-param": "error",
      "jsdoc/require-returns": "error",
      // biome-ignore lint/style/noMagicNumbers: ESLint rule configuration value
      complexity: ["error", 20],
      // biome-ignore lint/style/noMagicNumbers: ESLint rule configuration value
      "max-depth": ["error", 4],
      // biome-ignore lint/style/noMagicNumbers: ESLint rule configuration value
      "max-params": ["error", 4],
    },
  },
  {
    files: ["ts/*.d.ts"],
    rules: {
      "unicorn/no-keyword-prefix": "error",
    },
  },
];
