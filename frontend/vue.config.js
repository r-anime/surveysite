module.exports = {
    publicPath: '/static/vue/',
    outputDir: './dist/static/vue/',
    indexPath: '../../templates/index.html', // Relative to outputDir
    pages: {
        index: {
            entry: 'src/main.ts',
            title: '/r/anime Surveys',
        },
    },
}