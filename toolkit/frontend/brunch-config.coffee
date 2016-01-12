module.exports = config:
  paths:
    public: '../miRNA/static'
  files:
    javascripts: joinTo:
      'libraries.js': /^(?!app\/)/
      'app.js': /^app\//
    stylesheets:
      joinTo:
        'libraries.css': /^bower_components\//
        'app.css': /^(app|bower_components)/
      order:
        before: ['bower_components/normalize-css/normalize.css']
  plugins:
    coffeescript:
      bare: true
    sass:
      mode: 'ruby'
    autoReload:
      enabled: true
  conventions:
    assets: /^app[\\/]assets[\\/]/
