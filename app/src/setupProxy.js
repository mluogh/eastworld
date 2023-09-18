// Unfortunately, this doesn't support ts
// See: https://github.com/facebook/create-react-app/issues/6794
const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function (app) {
  app.use(
    "/api",
    createProxyMiddleware({
      // Needs to be 127.0.0.1 for mac?
      // https://github.com/facebook/create-react-app/discussions/10149
      target: "http://127.0.0.1:8000",
      changeOrigin: true,
      pathRewrite: {
        "^/api": "", // Remove /api from path
      },
    }),
  );
};
