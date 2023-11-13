/* eslint-env node */
require("@rushstack/eslint-patch/modern-module-resolution");

module.exports = {
  root: true,
  extends: [
    "plugin:vue/vue3-essential",
    "eslint:recommended",
    "@vue/eslint-config-typescript/recommended",
    // "@vue/eslint-config-prettier", Do something with this in the future
  ],
  rules: {
    indent: ["warn", 2, { SwitchCase: 1 }],
    semi: ["error", "always"],
    "semi-style": ["error", "last"],
    "vue/multi-word-component-names": ["warn", {}], // TODO: Remove after names are fixed
  },
};
