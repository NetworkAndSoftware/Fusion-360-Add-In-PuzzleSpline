# Fusion-360-Add-In-PuzzleSpline
Fusion 360 Add-in that creates a pair of toothed curves that can be used to split a body and create two pieces that slide and lock together.

## Installation

Download all this entire package, copy it to the Fustion Add-In directory or any location of your choosing, then in Fusion, go to TOOLS panel, choose Add-Ins, go to the Add-Ins tab, click the + icon and point it at the directory where you put the files. Then hit Run and possibly check "Run on Startup". When the add is running, this will add an icon to the "Construct" menu in the SOLID panel.

## Usage
Decide which plane you want to create the spline on. You can choose one of the origin planes or create a construction plane. Then choose "Puzzle Spline" on the CONSTRUCT menu in the SOLID work panel. Now select the plane that you picked and you should see a preview. Adjust to your liking and click OK. Now go to the SURFACE panel, select all of the splines that were generated and extrude a double surface. Then, back to the SOLID panel and choose Split Body in the MODIFY menu and pick the body that you want to split and the surfaces that you just made. Now you should end up with bodies for both sides and a thinner one in the middle that you'll probably want to discard. 

![Screenshot](screenshot.png)

![Example Result](ball.png)