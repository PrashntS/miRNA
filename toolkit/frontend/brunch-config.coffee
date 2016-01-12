module.exports = config:
  paths:
    public: '../miRNA/static'
  files:
    javascripts: joinTo:
      'libraries.js': /^(?!app\/)/
      'app.js': /^app\//
    stylesheets: joinTo: 'app.css'
  plugins:
    coffeescript:
      bare: true
    sass:
      mode: 'ruby'
