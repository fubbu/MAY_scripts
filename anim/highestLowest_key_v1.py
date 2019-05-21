import maya.cmds as cm
import maya.mel as mel
from math import floor

axisL = ("X","Y","Z")
axisS = ("x","y","z")


def HIGHEST_LOWEST_KEY_DB(void):
	channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
	attrs = cm.channelBox(channelBox, q=1, sma=1)
	keyMid = cm.intField(keyBt,q=1,v=1)
	listCurveKey = []

	objSel = cm.ls(sl=1,fl=1)
	if (attrs is None):
		cm.confirmDialog(m="!!! select any channel !!!")
		return
	for i in range(len(attrs)):
		inputChannel = cm.listConnections("{}.{}".format(objSel[0],attrs[i]),d=0,s=1)
		if(inputChannel is None):
			cm.confirmDialog(m="!!! selected channel is empty / select channel with animation!!!")
			return
		else:
			listCurveKey.append(inputChannel[0])


	startSearch = cm.findKeyframe( ts=1, w="first" )
	endSearch = cm.findKeyframe( ts=1, w="last" )
	cm.currentTime(startSearch)

	for i in range(len(listCurveKey)):
		keyNumber = cm.keyframe(listCurveKey[i],iv=1,q=1)
		listKey = []
		for m in range(len(keyNumber)):
			valKey = cm.getAttr("{}.keyTimeValue[{}]".format(listCurveKey[i],m))
			listKey.append(valKey)

		for m in range(len(listKey)-1):
					lowVal = 'none'
					lowKey = 'none'
					highVal = 'none'
					highKey = 'none'

					valS = listKey[m]
					valE = listKey[m+1]
					mergeVal = [valS[0][1],valE[0][1]]
					mergeVal.sort()

					if(keyMid > 0):
						sK = valS[0][0]
						eK = valE[0][0]

						midFrame = floor(((eK - sK)/(keyMid+1)))
						for n in range(keyMid):
							cm.currentTime((midFrame*(n+1))+sK)
							mel.eval('selectKey -add -k {} ;'.format(listCurveKey[i]))
							mel.eval('string $curves[] = `keyframe -q -selected -name`; int $i; for ($i = 0; $i < size($curves); $i++) {   float $curTime = `animCurveEditor -keyingTime $curves[$i] -q graphEditor1GraphEd`;    if ( size($curves) ) setKeyframe -time $curTime -insert $curves[$i]; }')

					
					cm.currentTime(valS[0][0])
					lowCheck = mergeVal[0]
					highCheck = mergeVal[1]

					while (cm.currentTime(q=1) < valE[0][0]):
						currentFrame = cm.currentTime(q=1)
						cm.currentTime(currentFrame+1)
						newValue = cm.getAttr("{}.{}".format(objSel[0],attrs[i]))

						if(newValue < lowCheck):
							lowVal = newValue
							lowCheck = newValue
							lowKey = cm.currentTime(q=1)
							
						if(newValue > highCheck):
							highVal = newValue
							highCheck = newValue
							highKey = cm.currentTime(q=1)

					if not(lowKey == 'none'):
						cm.currentTime(lowKey)
						cm.setKeyframe( at='{}'.format(attrs[i]) )

					if not(highKey == 'none'):
						cm.currentTime(highKey)
						cm.setKeyframe( at='{}'.format(attrs[i]) )

def SPACE_SWITCH_BAKE_ANIM_DB(void):
	sSwitchV = cm.intField(spaceSwitchValue,q=1,v=1)
	locBakeList = []
	listCurveKey = []
	blockLastChannel = ["tx","ty","tz","rx","ry","rz","sx","sy","sz","v"]
	checkChannel = ["tx","ty","tz","rx","ry","rz"]
	#-------------------------------------------------------

	listSel = cm.ls(sl=1,fl=1)
	startBake = cm.playbackOptions(min=1,q=1)
	endBake = cm.playbackOptions(max=1,q=1)
	channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
	attrs = cm.channelBox(channelBox, q=1, sma=1)
	if not (attrs is None):
		checkSelection = len(attrs)
		if(checkSelection == 1):
			cm.confirmDialog(m="select at least two channels !!!  last selected channel must be space switch channel  !!!")
			return
	else:
		cm.confirmDialog(m="select at least two channels !!!  last selected channel must be space switch channel  !!!")
		return

	if(attrs[-1] in blockLastChannel):
		cm.confirmDialog(m="!!!  last selected channel must be space switch channel  !!!")
		return

	checkChannelSelection = [x for x in checkChannel if x in attrs]
	if(len(checkChannelSelection) != 6):
		checkChannelSelection = [x for x in checkChannel if not x in checkChannelSelection]
		confirm = cmds.confirmDialog( title='Confirm', message='{} wasnt selected'.format(checkChannelSelection), button=['continue','break'] )
		if (confirm == "break"):
			return

	for i in range(len(listSel)):
		locBake = "locBake_anim_DB_{}".format(i)
		#-------------------------------------------------------

		cm.spaceLocator(n = locBake)
		locBakeList.append(locBake)
		cm.parentConstraint(listSel[i],locBake)
		for n in range(len(attrs)):
			inputChannel = cm.listConnections("{}.{}".format(listSel[i],attrs[n]),d=0,s=1)
			if not (inputChannel is None):
				listCurveKey.append(inputChannel[0])

	cm.select(locBakeList)
	cm.bakeResults( 'locBake_anim_DB_*', t=(startBake,endBake), sm=1, sb=1, sr=1 )
		
	for i in range(len(listSel)):
		locBake = "locBake_anim_DB_{}".format(i)
		#-------------------------------------------------------

		if cm.objExists("{}_{}".format(listSel[i],attrs[-1])):
			cm.delete("{}_{}".format(listSel[i],attrs[-1]))
		cm.delete("{}_parentConstraint1".format(locBake))
		cm.setAttr("{}.{}".format(listSel[i],attrs[-1]),sSwitchV)

		cm.select(locBake)
		startSearch = cm.findKeyframe(ts=1, w="first" )
		endSearch = cm.findKeyframe(ts=1, w="last" )
		numberOfKeys = cmds.keyframe(iv=1,q=1)
		numberOfKeys = list(set(numberOfKeys))
		cm.currentTime(startSearch)

		for m in range(len(numberOfKeys)):
			nextKey = cm.findKeyframe(ts=1, w="next" )
			parCon = cm.parentConstraint(locBakeList[i],listSel[i])
			for n in range(len(attrs)):	
				if [x for x in blockLastChannel if attrs[n] in x]:
					cm.setKeyframe("{}.{}".format(listSel[i],attrs[n]))
			cm.delete(parCon)
			cm.currentTime(nextKey)

		if cm.objExists(locBakeList[i]):
			cm.delete(locBakeList[i])
		mel.eval('hyperShadePanelBuildEditMenu hyperShadePanel1 hyperShadePanelMenuEditMenu;hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
				
#-------------------------------------WINDOW-------------------------------------
if cm.window('keyTransform_window',exists=1):
	cm.deleteUI('keyTransform_window')

keyTran_w = cm.window('keyTransform_window',t='highest lowest key')
mainWindow = cm.columnLayout(adj=3)
cm.separator(h=10,style='none')
cm.text('Add key between')
keyBt = cm.intField(min=0,v=0)
cm.separator(h=10,style='none')
cm.button(l='FIND KEYS',c=HIGHEST_LOWEST_KEY_DB,h=40)
cm.separator(h=20,style='none')
cm.text('!! last pick must by space switch channel !!')
cm.separator(h=10,style='none')
cm.text('Space switch value')
spaceSwitchValue = cm.intField(min=0,v=0)
cm.separator(h=10,style='none')
cm.button(l='SPACE SWITCH BAKE',c=SPACE_SWITCH_BAKE_ANIM_DB,h=40)

cm.showWindow(keyTran_w)