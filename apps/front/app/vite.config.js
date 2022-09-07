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
        host: true,
        port: 5173,
        proxy: {
        '/openbis/' : {
            ws: true,
            changeOrigin: true,
            secure: false,
            target: "http://openbis:443/openbis/openbis/"},
        '/data-discovery' : {
            ws: true,
            changeOrigin: true,
            secure: false,
            target: "http://data-discovery:80/",
            rewrite: (path) =>  path.replace(/^\/data-discovery/, "")
        }
    }
}
});