module.exports = config:
  paths:
    public: '../miRNA/static'
  files:
    javascripts: joinTo:
      'libraries.js': (path) ->
        /^(bower_components)|(lodash)\//.test path
      'app.js': (path) ->
        /^(app)\//.test path
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
  npm:
    enabled: yes
    whitelist: ['lodash']
  conventions:
    ignored: [
      /fontawesome/
    ]
