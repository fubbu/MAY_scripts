import maya.cmds as cm

axisL = ("X","Y","Z")
axisS = ("x","y","z")

listSel = cm.ls(sl=1,fl=1)
listSel = cm.listRelatives(listSel[0])

cm.shadingNode('follicle',au=1)
cm.pickWalk(d='up')
cm.rename("aaaa")
cm.rename("aaaa","follicle_aaaa_1")

follicleSel = cm.ls(sl=1,fl=1)
follicleSelShape = cm.listRelatives(follicleSel[0])

cm.connectAttr("{}.local".format(listSel[0]),"{}.inputSurface".format(follicleSelShape[0]))
cm.connectAttr("{}.worldMatrix[0]".format(listSel[0]),"{}.inputWorldMatrix".format(follicleSelShape[0]))

for i in range(3):
	cm.connectAttr("{}.outTranslate{}".format(follicleSelShape[0],axisL[i]),"{}.t{}".format(follicleSel[0],axisS[i]))
	cm.connectAttr("{}.outRotate{}".format(follicleSelShape[0],axisL[i]),"{}.r{}".format(follicleSel[0],axisS[i]))