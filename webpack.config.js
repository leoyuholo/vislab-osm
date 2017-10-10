const path = require('path')
const webpack = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const FriendlyErrors = require('friendly-errors-webpack-plugin')

module.exports = {
  entry: './app/main.js',
  resolve: {
    extensions: ['.vue', '.js', '.json'],
    alias: {
      vue: 'vue/dist/vue.js'
    }
  },
  output: {
    path: path.join(__dirname, '/static/'),
    filename: '[name].js',
    publicPath: '/'
  },
  devtool: '#cheap-module-eval-source-map',
  devServer: {
    contentBase: './static/',
    // hot: true,
    host: '0.0.0.0',
    port: 3000,
    disableHostCheck: true,
    proxy: {
      "/api": {
        target: "http://flask:5000",
        pathRewrite: {"^/api": ""}
      }
    }
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: 'app/index.tpl.html',
      inject: 'body',
      filename: 'index.html'
    }),
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NamedModulesPlugin(),
    new webpack.NoEmitOnErrorsPlugin(),
    new FriendlyErrors()
  ],
  module: {
    loaders: [
      {
        test: /\.vue$/,
        // exclude: /node_modules/,
        use: [
          {
            loader: 'vue-loader',
            options: {
              loaders: {
                js: 'babel-loader',
                css: 'vue-style-loader!css-loader'
              }
            }
          }
        ]
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader'
        }
      }
    ]
  }
}
