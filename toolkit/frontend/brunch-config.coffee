module.exports = config:
  paths:
    public: '../miRNA/static'
  files:
    javascripts: joinTo:
      'libraries.js': /^bower_components\//
      'app.js': /^(app)\//
    stylesheets:
      joinTo:
        'libraries.css': /^bower_components\//
        'app.css': /^(app)/
      order:
        before: ['bower_components/normalize-css/normalize.css']
  plugins:
    coffeescript:
      bare: yes
    sass:
      mode: 'ruby'
      allowCache: true
      options:
        includePaths: (->
          bourbon = require('node-bourbon').includePaths
          neat = require('node-neat').includePaths
          bourbon.concat neat
        )()
    autoReload:
      enabled: yes
  conventions:
    ignored: [
      /fontawesome/
    ]
