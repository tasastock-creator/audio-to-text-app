import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2';
env.allowLocalModels = false;
env.useBrowserCache = true;
let pipe = null;
let loadedModel = '';
let busy = false;
function send(percent, message) { postMessage({ type: 'progress', percent, message }); }
async function load(config) {
  if (pipe && loadedModel === config.model) return;
  pipe = null;
  loadedModel = config.model;
  send(4, `Loading ${config.label} model…`);
  pipe = await pipeline('automatic-speech-recognition', config.model, {
    quantized: true,
    progress_callback: x => {
      if (x.status === 'progress') {
        const p = Math.round(x.progress || 0);
        send(Math.min(65, 5 + p * 0.6), `Downloading/caching AI model: ${p}%`);
      }
    }
  });
  postMessage({ type: 'ready', model: loadedModel });
}
onmessage = async e => {
  const m = e.data;
  try {
    if (m.type === 'load') {
      await load(m.config);
      return;
    }
    if (m.type === 'transcribe') {
      if (busy) throw new Error('A transcription is already running.');
      busy = true;
      await load(m.config);
      send(70, `Transcribing all ${Math.round(m.audio.length / 16000)} seconds in background…`);
      const opts = {
        chunk_length_s: 30,
        stride_length_s: 5,
        return_timestamps: true,
        task: 'transcribe'
      };
      if (m.language && m.language !== 'auto') opts.language = m.language;
      const out = await pipe(m.audio, opts);
      const text = (out && out.text) ? out.text : '';
      postMessage({ type: 'result', text, chunks: out?.chunks || [] });
      busy = false;
    }
  } catch (err) {
    busy = false;
    postMessage({ type: 'error', message: err?.message || String(err) });
  }
};
