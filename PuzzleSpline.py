#Author-Michiel van Wessem
#Description-Creates a pair of toothed curves that can be used to split a body and create two pieces that slide and lock together.

import adsk.core
import adsk.fusion
import traceback

handlers = []
ui = None
deleteMes = []


IdCommandButton = 'PuzzleSplineId12'
idWidth = "idWidth"
idHeight = "idHeight"
idPlane = "plane"

count = 4
clearance = .05
plane = None
width = 4
height = .1

def run(context):
    global ui
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        buttonDefinition = ui.commandDefinitions.addButtonDefinition(IdCommandButton,
                                                   'Puzzle Spline',
                                                   'Creates a sketch with a two offset splines that can be used for splitting solids',
                                                   './/Resources/PuzzleSplineButton')
        deleteMes.append(buttonDefinition)

        # Connect to the command created event.
        myCommandCreated = MyCommandCreatedEventHandler()
        buttonDefinition.commandCreated.add(myCommandCreated)
        handlers.append(myCommandCreated)

        workspace = ui.workspaces.itemById('FusionSolidEnvironment')

        panel = workspace.toolbarPanels.itemById('ConstructionPanel')
        deleteMes.append(panel.controls.addSeparator())
        deleteMes.append(panel.controls.addCommand(buttonDefinition))
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class EventHandlerWithExceptionReporting():
  def __init__(self):
    self.oldNotify = self.notify
    self.notify = self.newNotify

  def newNotify(self, args):
    try:
      self.oldNotify(args)
    except:
      if ui:
        ui.messageBox('Exception in event handler:\n{}'.format(traceback.format_exc()))


class MyCommandDestroyHandler(adsk.core.CommandEventHandler, EventHandlerWithExceptionReporting):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            eventArgs = adsk.code.CommandEventArgs.cast(args)
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            # adsk.terminate()
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MyCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler, EventHandlerWithExceptionReporting):
    def __init__(self):
      EventHandlerWithExceptionReporting.__init__(self)
      super().__init__()

    def notify(self, args):
      eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
      cmd = adsk.core.Command.cast(eventArgs.command)

      cmd.isOKButtonVisible = True

      onExecutePreview = MyCommandExecutePreviewHandler()
      cmd.executePreview.add(onExecutePreview)
      handlers.append(onExecutePreview)

      onInputChanged = MyInputChangedHandler()
      cmd.inputChanged.add(onInputChanged)
      handlers.append(onInputChanged)

      # Get the CommandInputs collection associated with the command.
      inputs = cmd.commandInputs

      selectionInput = inputs.addSelectionInput(
        idPlane, "Plane", "Select plane")
      selectionInput.addSelectionFilter('ConstructionPlanes')
      selectionInput.setSelectionLimits(1, 1)
      selectionInput.tooltipDescription = 'Please select a plane to generate the splines on'

      inputs.addIntegerSpinnerCommandInput(
        'count', 'Loop count', 1, 100, 1, count)

      clearanceSlider = adsk.core.FloatSliderCommandInput.cast(
        inputs.addFloatSliderCommandInput('clearance', 'Clearance', 'mm', .02, .2))
      clearanceSlider.valueOne = clearance
      clearanceSlider.tooltipDescription = 'This is the distance between the two generated splines'

      widthInput = inputs.addDistanceValueCommandInput(
        idWidth, "Width", adsk.core.ValueInput.createByReal(width))
      heightInput = adsk.core.DistanceValueCommandInput.cast(inputs.addDistanceValueCommandInput(
        idHeight, "Height", adsk.core.ValueInput.createByReal(height)))
      widthInput.isEnabled = False
      heightInput.isEnabled = False
      heightInput.minimumValue = 0
      heightInput.isMinimumValueInclusive = False

class MyInputChangedHandler(adsk.core.InputChangedEventHandler, EventHandlerWithExceptionReporting):
    def __init__(self):
      EventHandlerWithExceptionReporting.__init__(self)
      super().__init__()

    def notify(self, args):
      global plane
      eventArgs = adsk.core.InputChangedEventArgs.cast(args)
      inputs = eventArgs.inputs
      input = eventArgs.input
      if input.id == idPlane:

        widthInput = inputs.itemById(idWidth)
        heightInput = inputs.itemById(idHeight)
        
        b = input.selectionCount == 1
        widthInput.isEnabled = b
        heightInput.isEnabled = b

        if not b:
          plane = None
          return

        plane = input.selection(0).entity
        geometry = plane.geometry
        
        # organ = adsk.core.Point3D.create(10,10,10)
        # dir = adsk.core.Vector3D.create(20,20,20)
        a = widthInput.setManipulator(geometry.origin, geometry.uDirection)
        b = heightInput.setManipulator(geometry.origin, geometry.vDirection)            


class MyCommandExecutePreviewHandler(adsk.core.CommandEventHandler, EventHandlerWithExceptionReporting):
    def __init__(self):
      EventHandlerWithExceptionReporting.__init__(self)
      super().__init__()

    def notify(self, args):
        global count, ui, plane, clearance, width, height


        eventArgs = adsk.core.CommandEventArgs.cast(args)
        eventArgs.isValidResult = False

        inputs = eventArgs.command.commandInputs

        count = inputs.itemById('count').value

        clearanceInput = adsk.core.FloatSliderCommandInput.cast(
            inputs.itemById('clearance'))
        clearance = clearanceInput.valueOne

        widthInput = adsk.core.DistanceValueCommandInput.cast(
            inputs.itemById(idWidth))
        width = widthInput.value

        heightInput = adsk.core.DistanceValueCommandInput.cast(
            inputs.itemById(idHeight))
        height = heightInput.value

        planeInput = adsk.core.SelectionCommandInput.cast(
            inputs.itemById('plane'))
        if planeInput.selectionCount != 1:
            return

        drawPreview()

        eventArgs.isValidResult = True


def stop(context):
    try:
        app = adsk.core.Application.get()
        global ui

        for deleteMe in deleteMes:
          deleteMe.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def drawPreview():
    global plane, count, nominator

    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)

    # doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    # design = app.activeProduct

    if design:
        root = design.rootComponent
        
        sketch = root.sketches.add(plane)
        
        points = adsk.core.ObjectCollection.create()

        nominator = (21 * count, 7)
        for i in range(0, count):  # eg 0 1 2 3
            o = i / count  # 0/4 1/4 2/4 3/4

            def scale(p): return (
                width * (o + p[0] / nominator[0]), height * p[1] / nominator[1])

            for t in [(0, 0), (7, 2), (5, 5), (11, 7), (17, 5), (15, 2)]:
                p = scale((t[0], t[1]))
                point = adsk.core.Point3D.create(p[0], p[1], 0)
                points.add(point)

        point = adsk.core.Point3D.create(width, 0, 0)
        points.add(point)

        spline = sketch.sketchCurves.sketchFittedSplines.add(points)
        spline.isConstruction = True

        curves = sketch.findConnectedCurves(spline)

        directionPoint = adsk.core.Point3D.create(5, 10, 0)
        sketch.offset(curves, directionPoint, clearance / 2)
        sketch.offset(curves, directionPoint, - clearance / 2)
