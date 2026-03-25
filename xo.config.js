import jsdocPlugin from "eslint-plugin-jsdoc";

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
            FunctionDeclaration: true,
            MethodDefinition: true,
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
      "complexity": ["error", 20],
      "max-depth": ["error", 4],
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
