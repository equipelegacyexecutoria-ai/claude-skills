import {defineConfig} from 'vite';
import {createRequire} from 'module';
import {fileURLToPath} from 'url';
import path from 'path';

// O plugin do Motion Canvas é CommonJS: importar com require evita o erro de import em projeto ESM.
const require = createRequire(import.meta.url);
const motionCanvas = require('@motion-canvas/vite-plugin').default;
const ffmpeg = require('@motion-canvas/ffmpeg').default;

// Caminho absoluto: o servidor pode ser iniciado de outra pasta.
const raiz = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  root: raiz,
  plugins: [motionCanvas({project: path.join(raiz, 'src/project.ts').replace(/\\/g, '/')}), ffmpeg()],
});
