const path = require("path");
const webpack = require("webpack");
const BundleTracker = require("webpack-bundle-tracker");
const mode = process.env.NODE_ENV || "development";
const CompressionPlugin = require("compression-webpack-plugin");

module.exports = {
	devtool: (mode === 'development') ? 'inline-source-map' : false,
	mode: mode,
	context: __dirname,
	entry: {
		tictactoe: './templates/components/tictactoe/index',
		obstruction: './templates/components/obstruction/index',
		ludo: './templates/components/ludo/index',
		battleship: './templates/components/battleship/index',
		connect4: './templates/components/connect4/index',
		othello: './templates/components/othello/index',
	},
	output: {
		path: path.resolve("./static/bundles/"),
		filename: "[name]-[fullhash].js",
		clean: true,
	},
	plugins: [
		new webpack.HotModuleReplacementPlugin(),
		new webpack.NoEmitOnErrorsPlugin(),
		new CompressionPlugin(),
		new BundleTracker({path: __dirname, filename: "./webpack-stats.json"})
	],
	module: {
		rules: [{
			test: /\.jsx$/,
			exclude: /(node_modules)/,
			use: {
				loader: "babel-loader",
				options: {
					presets: ["@babel/preset-env", "@babel/preset-react"]
				}
			}
		}]
	},
	resolve: {
		modules: [__dirname, "node_modules"],
		extensions: ["", ".js", ".jsx"]
	},
}
