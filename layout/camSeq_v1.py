import maya.cmds as cm
import fnmatch

axisL = ("X","Y","Z")
axisS = ("x","y","z")

def SEARCH_CAMERS_DB():
	allSceneCamera_DB = cm.ls(type=('camera'), sn=1)
	filteredCamera_DB = cm.listRelatives(allSceneCamera_DB, p=1, f=1)
	filteredCamera_DB = [x.split('|')[-1] for x in filteredCamera_DB]
	global listShotsCamera_DB
	listShotsCamera_DB = fnmatch.filter(filteredCamera_DB, 'cam_S??U*')

	for i in range(len(listShotsCamera_DB)):
		pM_allShot = "pm_{}_range".format(listShotsCamera_DB[i])
		rV_allShot = "rv_{}_range".format(listShotsCamera_DB[i])
		#-------------------------------------------------------

		if cm.objExists(pM_allShot):
			cm.delete(pM_allShot)
		if cm.objExists(rV_allShot):
			cm.delete(rV_allShot)
		if cm.objExists('allShot_frame_expression'):
			cm.delete('allShot_frame_expression')

SEARCH_CAMERS_DB()

def LOCK_TRANSLATE_ROTATE_CAMERA_DB(i_obj,i_lock):
	lockVal = 0
	if(i_lock == 1):
		lockVal = 1
	for i in range(3):
		cm.setAttr("{}.t{}".format(i_obj,axisS[i]),l=lockVal)
		cm.setAttr("{}.r{}".format(i_obj,axisS[i]),l=lockVal)
		cm.setAttr("{}.s{}".format(i_obj,axisS[i]),l=lockVal)

def LOCK_ST_ET_CAMERA_DB(i_obj,i_lock):
	cm.setAttr("{}.startShotRange".format(i_obj),l=i_lock)
	cm.setAttr("{}.endShotRange".format(i_obj),l=i_lock)

def CREATE_MAIN_SEQ_CAM_DB():
	global selectedCamera_DB
	sT = 'startShotRange'
	eT = 'endShotRange'
	MC = "sequenceCameraMain"
	parMC = "sequenceCameraMain_parentConstraint1"

	if (selectedCamera_DB == -1):
		startTime = cm.getAttr("{}.{}".format(listShotsCamera_DB[0],sT))
		endTime = cm.getAttr("{}.{}".format(listShotsCamera_DB[0],eT))

		cm.playbackOptions(min=startTime,max=endTime)
	selectedCamera_DB = 0
	#-------------------------------------------------------
	
	if(len(listShotsCamera_DB) == 0):
		return
	if cm.objExists(MC):
		cm.setAttr("{}.v".format(MC),0)
		checkAttr = cm.attributeQuery("currentFrame",n=MC,ex=1)
		if(checkAttr == 0):
			cm.addAttr(MC,ln="currentFrame",at='double',dv=0,keyable=1)
		LOCK_TRANSLATE_ROTATE_CAMERA_DB(MC,0)
		if cm.objExists(parMC):	
			for i in range(len(listShotsCamera_DB)):
				testCam = 0
				checkAttr = cm.attributeQuery("{}W{}".format(listShotsCamera_DB[i],i),n=parMC,ex=1)
				if(checkAttr == 1):
					testCam = cm.getAttr("{}.{}W{}".format(parMC,listShotsCamera_DB[i],i))
				if(testCam == 1):
					selectedCamera_DB = i
			cm.delete(parMC)

		CAMERA_SEQ_PARENT_DB(MC,parMC)

		cm.setAttr("{}.{}W{}".format(parMC,listShotsCamera_DB[selectedCamera_DB],selectedCamera_DB),1)
		LOCK_TRANSLATE_ROTATE_CAMERA_DB(MC,1)

	else:
		cm.camera()
		cm.rename("aaaabbbb")
		cm.rename("aaaabbbb",MC)
		cm.addAttr(MC,ln="currentFrame",at='double',dv=0,keyable=1)

		CAMERA_SEQ_PARENT_DB(MC,parMC)

		cm.setAttr("{}.{}W{}".format(parMC,listShotsCamera_DB[0],0),1)
		LOCK_TRANSLATE_ROTATE_CAMERA_DB(MC,1)
		cm.setAttr("{}.v".format(MC),0)

def CAMERA_SEQ_PARENT_DB(i_mc,i_parmc):
	global selectedCamera_DB
	sT = 'startShotRange'
	eT = 'endShotRange'
	#-------------------------------------------------------

	for i in range(len(listShotsCamera_DB)):
		cm.parentConstraint(listShotsCamera_DB[i], i_mc)
		cm.setAttr("{}.{}W{}".format(i_parmc ,listShotsCamera_DB[i],i),0)
		checkAttr = cm.attributeQuery(sT,n=listShotsCamera_DB[i],ex=1)
		if(checkAttr == 0):
			cm.addAttr(listShotsCamera_DB[i],ln=sT,at='double',dv=0,keyable=1)
			cm.addAttr(listShotsCamera_DB[i],ln=eT,at='double',dv=200,keyable=1)
		LOCK_ST_ET_CAMERA_DB(listShotsCamera_DB[i],1)


CREATE_MAIN_SEQ_CAM_DB()
	
def CHECK_CAMERA_SHOT_RANGE():
	sT = 'startShotRange'
	eT = 'endShotRange'
	#-------------------------------------------------------

	if not (selectedCamera_DB == -1):
		startTime = cm.playbackOptions(min=1,q=1)
		endTime = cm.playbackOptions(max=1,q=1)
		checkS = cm.getAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB],sT))
		checkE = cm.getAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB],eT))

		if(startTime != checkS or endTime != checkE):
			confirm = cmds.confirmDialog( title='Confirm', message='Camera shot range doesnt match timeslider', button=['update shot range','leave'] )

			if (confirm == "update shot range"):
				WRITE_SHOT_RANGE_DB()

def CAMERA_SEQ_CHANGE_DB(i_cam):
	global selectedCamera_DB
	MC = "sequenceCameraMain"
	parMC = "sequenceCameraMain_parentConstraint1"
	sT = 'startShotRange'
	eT = 'endShotRange'
	#-------------------------------------------------------

	if (i_cam == "allShots"):
		selectedCamera_DB = -1
		CHECK_CAMERA_SHOT_RANGE()
		playTime = []
		for i in range(len(listShotsCamera_DB)):
			pM_allShot = "pm_{}_range".format(listShotsCamera_DB[i])
			rV_allShot = "rv_{}_range".format(listShotsCamera_DB[i])
			#-------------------------------------------------------

			cm.shadingNode("plusMinusAverage",au=1,n=pM_allShot)
			cm.shadingNode("remapValue",au=1,n=rV_allShot)
			cm.connectAttr("{}.{}".format(listShotsCamera_DB[i],sT),"{}.input2D[0].input2Dx".format(pM_allShot))
			cm.connectAttr("{}.{}".format(listShotsCamera_DB[i],eT),"{}.input2D[0].input2Dy".format(pM_allShot))
			cm.setAttr("{}.input2D[1].input2Dx".format(pM_allShot),-1)
			cm.setAttr("{}.input2D[1].input2Dy".format(pM_allShot),1)
			cm.connectAttr("{}.output2Dx".format(pM_allShot),"{}.inputMax".format(rV_allShot))
			cm.connectAttr("{}.output2Dy".format(pM_allShot),"{}.inputMin".format(rV_allShot))
			cm.connectAttr("{}.currentFrame".format(MC),"{}.inputValue".format(rV_allShot))
			cm.connectAttr("{}.outValue".format(rV_allShot),"{}.{}W{}".format(parMC,listShotsCamera_DB[i],i))
			mel.eval('setAttr {0}.value[0].value_FloatValue 0;setAttr "{0}.value[0].value_Interp" 1;setAttr {0}.value[0].value_Position 0;setAttr {0}.value[1].value_FloatValue 1;setAttr "{0}.value[1].value_Interp" 1;setAttr {0}.value[1].value_Position 0.001;setAttr {0}.value[2].value_FloatValue 1;setAttr "{0}.value[2].value_Interp" 1;setAttr {0}.value[2].value_Position 0.999;setAttr {0}.value[3].value_FloatValue 0;setAttr "{0}.value[3].value_Interp" 1;setAttr {0}.value[3].value_Position 1;'.format(rV_allShot))
			playTime.append(cm.getAttr("{}.{}".format(listShotsCamera_DB[i],sT)))
			playTime.append(cm.getAttr("{}.{}".format(listShotsCamera_DB[i],eT)))

		cm.expression(n='allShot_frame_expression',s='sequenceCameraMain.currentFrame = frame;' )
		playTime.sort()
		cm.playbackOptions(min=playTime[0],max=playTime[-1])

	else:
		if not (selectedCamera_DB == -1):
			CHECK_CAMERA_SHOT_RANGE()

			cm.setAttr("{}.{}W{}".format(parMC,listShotsCamera_DB[selectedCamera_DB],selectedCamera_DB),0)
		else:
			for i in range(len(listShotsCamera_DB)):
				pM_allShot = "pm_{}_range".format(listShotsCamera_DB[i])
				rV_allShot = "rv_{}_range".format(listShotsCamera_DB[i])
				#-------------------------------------------------------

				cm.delete(pM_allShot,rV_allShot)
				cm.setAttr("{}.{}W{}".format(parMC,listShotsCamera_DB[i],i),0)

			cm.delete('allShot_frame_expression')

		selectedCamera_DB = listShotsCamera_DB.index("{}".format(i_cam))

		cm.setAttr("{}.{}W{}".format(parMC,i_cam,selectedCamera_DB),1)

		startTime = cm.getAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB],sT))
		endTime = cm.getAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB],eT))

		cm.playbackOptions(min=startTime,max=endTime)

def WRITE_SHOT_RANGE_DB(*args):
	global selectedCamera_DB
	sT = 'startShotRange'
	eT = 'endShotRange'
	#-------------------------------------------------------

	LOCK_ST_ET_CAMERA_DB(listShotsCamera_DB[selectedCamera_DB],0)
	startTime = cm.playbackOptions(min=1,q=1)
	endTime = cm.playbackOptions(max=1,q=1)
	cm.setAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB],sT),startTime)
	cm.setAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB],eT),endTime)
	LOCK_ST_ET_CAMERA_DB(listShotsCamera_DB[selectedCamera_DB],1)




#-------------------------------------WINDOW-------------------------------------
if(len(listShotsCamera_DB) == 0):
		cm.confirmDialog(m="!!!  there is no sequence camera in scene  !!!")
else:
	if cm.window('seqCam_window',exists=1):
		cm.deleteUI('seqCam_window')

	window = cm.window('seqCam_window',t='Sequence Camers')
	cm.columnLayout()
	cm.separator(h=10,style='none')
	opM = cm.optionMenu( l='Camers',cc=CAMERA_SEQ_CHANGE_DB )
	for i in range(len(listShotsCamera_DB)):
		cm.menuItem( l=listShotsCamera_DB[i] )
	cm.menuItem( l="allShots" )
	cm.optionMenu( opM,e=1,sl=selectedCamera_DB+1 )

	cm.separator(h=10,style='none')
	cm.button(l='WRITE SHOT RANGE',c=WRITE_SHOT_RANGE_DB,h=40,w=170)
	cm.showWindow( window )