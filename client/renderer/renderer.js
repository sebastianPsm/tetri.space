const ex = require('excalibur');

var game = new ex.Engine({ })
// todo build awesome game here

var paddle = new ex.Actor(150, game.drawHeight - 40, 200, 20)
paddle.color = ex.Color.Chartreuse
paddle.collisionType = ex.CollisionType.Fixed
game.add(paddle)

// Start the engine to begin the game.
game.start()