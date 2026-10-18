// dependency-cruiser rules for a React app: components render, hooks fetch through the API client.
// Copy to web/.dependency-cruiser.cjs; in the gate run `pnpm exec depcruise --config .dependency-cruiser.cjs src`
// with dependency-cruiser and typescript as devDependencies (without typescript, .ts files are silently skipped).
// Tested with dependency-cruiser 18.4.0; 16.x crashes on Node 26.
/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: "no-circular",
      severity: "error",
      comment: "Import cycles make modules impossible to understand or test alone.",
      from: {},
      to: { circular: true },
    },
    {
      name: "components-not-to-api",
      severity: "error",
      comment: "Components take props; data fetching goes through hooks that call the API client.",
      from: { path: "^src/components/" },
      to: { path: "^src/api/" },
    },
  ],
  options: {
    doNotFollow: { path: "node_modules" },
    tsPreCompilationDeps: false,
  },
};
