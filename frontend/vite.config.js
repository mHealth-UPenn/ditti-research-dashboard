/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import svgr from "vite-plugin-svgr";

// Intercepts Firefox React DevTools .map requests and returns a minimal stub
const devToolsMapStub = {
  configureServer({ middlewares }) {
    middlewares.use((req, res, next) => {
      const m = req.url?.match(
        /(installHook|react_devtools_backend_compact)\.js\.map$/
      );
      if (!m) return next();
      const f = `${m[1]}.js`; // e.g. "installHook.js"
      res.setHeader("Content-Type", "application/json");
      res.end(
        `{"version":3,"file":"${f}","sources":["${f}"],"sourcesContent":[""],"mappings":""}`
      );
    });
  },
};

export default defineConfig({
  plugins: [svgr(), react(), tsconfigPaths(), devToolsMapStub],
  server: {
    port: 3000,
  },
});
