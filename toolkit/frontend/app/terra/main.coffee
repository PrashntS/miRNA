Terrarium = require('./terrarium')
factory = require('./creature')
module.exports =
  Terrarium: Terrarium
  make: factory.make
  registerCreature: factory.registerCreature
  registerCA: factory.registerCA
