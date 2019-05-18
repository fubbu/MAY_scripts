import maya.cmds as cm
import fnmatch

axisL = ("X","Y","Z")
axisS = ("x","y","z")

def SEARCH_CAMERS_DB():
	allSceneCamera_DB = cm.ls(type=('camera'), sn=1)
	filteredCamera_DB = cm.listRelatives(allSceneCamera_DB, p=1, f=1)
	global listShotsCamera_DB
	listShotsCamera_DB = fnmatch.filter(filteredCamera_DB, '|cam_S??U*')
	

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
	selectedCamera_DB = 0
	MC = "sequenceCameraMain"
	parMC = "sequenceCameraMain_parentConstraint1"
	#-------------------------------------------------------

	if cm.objExists(MC):
		LOCK_TRANSLATE_ROTATE_CAMERA_DB(MC,0)
		if cm.objExists(parMC):	
			for i in range(len(listShotsCamera_DB)):
				testCam = 0
				checkAttr = cm.attributeQuery("{}W{}".format(listShotsCamera_DB[i][1:],i),n=parMC,ex=1)
				if(checkAttr == 1):
					testCam = cm.getAttr("{}.{}W{}".format(parMC,listShotsCamera_DB[i][1:],i))
				if(testCam == 1):
					selectedCamera_DB = i
			cm.delete(parMC)

		CAMERA_SEQ_PARENT_DB(MC,parMC)

		cm.setAttr("{}.{}W{}".format(parMC,listShotsCamera_DB[selectedCamera_DB][1:],selectedCamera_DB),1)
		LOCK_TRANSLATE_ROTATE_CAMERA_DB(MC,1)

	else:
		cm.camera()
		cm.rename("aaaabbbb")
		cm.rename("aaaabbbb",MC)

		CAMERA_SEQ_PARENT_DB(MC,parMC)

		cm.setAttr("{}.{}W{}".format(parMC,listShotsCamera_DB[0][1:],0),1)
		LOCK_TRANSLATE_ROTATE_CAMERA_DB(MC,1)

def CAMERA_SEQ_PARENT_DB(i_mc,i_parmc):
	global selectedCamera_DB
	sT = 'startShotRange'
	eT = 'endShotRange'
	#-------------------------------------------------------

	for i in range(len(listShotsCamera_DB)):
		cm.parentConstraint(listShotsCamera_DB[i], i_mc)
		cm.setAttr("{}.{}W{}".format(i_parmc ,listShotsCamera_DB[i][1:],i),0)
		checkAttr = cm.attributeQuery(sT,n=listShotsCamera_DB[i][1:],ex=1)
		if(checkAttr == 0):
			cm.addAttr(listShotsCamera_DB[i][1:],ln=sT,at='double',dv=0,keyable=1)
			cm.addAttr(listShotsCamera_DB[i][1:],ln=eT,at='double',dv=200,keyable=1)
		LOCK_ST_ET_CAMERA_DB(listShotsCamera_DB[i][1:],1)


CREATE_MAIN_SEQ_CAM_DB()
	

def CAMERA_SEQ_CHANGE_DB(i_cam):
	global selectedCamera_DB
	parMC = "sequenceCameraMain_parentConstraint1"
	sT = 'startShotRange'
	eT = 'endShotRange'
	#-------------------------------------------------------

	startTime = cm.playbackOptions(min=1,q=1)
	endTime = cm.playbackOptions(max=1,q=1)
	checkS = cm.getAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB][1:],sT))
	checkE = cm.getAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB][1:],eT))

	if(startTime != checkS):
		confirm = cmds.confirmDialog( title='Confirm', message='Camera shot range doesnt match timeslider', button=['update shot range','leave'] )

		if (confirm == "update shot range"):
			WRITE_SHOT_RANGE_DB()

	cm.setAttr("{}.{}W{}".format(parMC,listShotsCamera_DB[selectedCamera_DB][1:],selectedCamera_DB),0)

	selectedCamera_DB = listShotsCamera_DB.index("|{}".format(i_cam))

	cm.setAttr("{}.{}W{}".format(parMC,i_cam,selectedCamera_DB),1)

	startTime = cm.getAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB][1:],sT))
	endTime = cm.getAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB][1:],eT))

	cm.playbackOptions(min=startTime,max=endTime)

def WRITE_SHOT_RANGE_DB():
	global selectedCamera_DB
	sT = 'startShotRange'
	eT = 'endShotRange'
	#-------------------------------------------------------

	LOCK_ST_ET_CAMERA_DB(listShotsCamera_DB[selectedCamera_DB][1:],0)
	startTime = cm.playbackOptions(min=1,q=1)
	endTime = cm.playbackOptions(max=1,q=1)
	cm.setAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB][1:],sT),startTime)
	cm.setAttr("{}.{}".format(listShotsCamera_DB[selectedCamera_DB][1:],eT),endTime)
	LOCK_ST_ET_CAMERA_DB(listShotsCamera_DB[selectedCamera_DB][1:],1)




#-------------------------------------WINDOW-------------------------------------
if(listShotsCamera_DB is None):
	cm.confirmDialog(m="!!!  there is no sequence camera in scene  !!!")
else:
	if cm.window('seqCam_window',exists=1):
		cm.deleteUI('seqCam_window')

	window = cm.window('seqCam_window',t='Sequence Camers')
	cm.columnLayout()
	cm.separator(h=10,style='none')
	opM = cm.optionMenu( l='Camers',cc=CAMERA_SEQ_CHANGE_DB )
	for i in range(len(listShotsCamera_DB)):
		cm.menuItem( l=listShotsCamera_DB[i][1:] )
	cm.optionMenu( opM,e=1,sl=selectedCamera_DB+1 )

	cm.separator(h=10,style='none')
	cm.button(l='WRITE SHOT RANGE',c=WRITE_SHOT_RANGE_DB,h=40,w=170)
	cm.showWindow( window )