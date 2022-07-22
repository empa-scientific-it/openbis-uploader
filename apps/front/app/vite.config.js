import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

//Resolve @
const path = require("path");
export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        proxy: {
        '/openbis' : {
            ws: true,
            changeOrigin: true,
            secure: false,
            target: "https://localhost:8443/openbis/openbis/"}
        }
    }
});