# Calibration Shapes Reborn
A continuation of [Calibration Shapes by 5@xes](https://github.com/5axes/Calibration-Shapes/).

This plugin adds a menu to create some simple shapes to the scene (cube, sphere, cylinder, tube), custom bridging test shapes and calibration sample parts.

## Features:
### Simple shapes:
Quickly add basic shapes (cube, sphere, cylinder, tube) to your scene from the menu.  
The default size for the simple shapes is 20 mm, but can be modified via the *Set default size* menu option.
### Custom Bridging Tests:
Test your printer's ability to span voids of varying vastness with custom boxes, tubes and right angle triangles.
  - Tip: If you're making a bridging triangle, set *Top/Bottom > Top/Bottom Pattern* to *Lines* and set *Top/Bottom > Top/Bottom Line Directions* to *[0,90]* to test the triangle getting evenly further out each time.
### Calibration shapes:
Given the name, they had to be in here somewhere! Print these models designed to test various aspects of your printer's performance. Information about what they do can be found [in the documentation for the original version of the plugin](https://github.com/5axes/Calibration-Shapes/wiki) - just bear in mind that I've removed a few things if something looks missing (see below for more details).

---
### Changelog:
#### 1.1.0
- Added custom bridging shapes (box, tube, triangle) from an audience request.  
See, I want your ideas! Please send them in.
- Dead code continues to be removed. With the cleaning up I've done this time, it'll run *imperceptibly* faster.
#### 1.0.2
- Removed a function call that caused errors in Cura 5.0 and 5.1.
- More sweeping up dead code, but now it'll use less RAM because of it.
#### 1.0.1 (initial published release)
- Replaced the "default size" dialog with something far less disruptive and fitting in with Cura's UI style.
- Fixed a few typos in the code which may have affected things in some cases.
- Still sweeping up dead code.
#### 1.0.0
- Changed name in all the code so that it doesn't interact with the original version if you happen to have them side by side.
- All the changes in the "removed features" section below, including removing dead code related to them.

---
**This version has removed several features available in the original to be easier for me to maintain:**
- *Now requires Cura 5.0 or higher.* This has allowed me to remove legacy code.
- Test towers are gone. [AutoTowers Generator](https://github.com/kartchnb/AutoTowersGenerator) does a far better job than I ever could.
- Any other calibration prints which relied on post-processing scripts have also been removed.
- Due to my changes the existing translation files won't work. Feel free to speak up if you'd like to help!

---
### If something isn't working, I want to know! Just create something in the [issues](https://github.com/Slashee-the-Cow/CalibrationShapesReborn/issues) page.
### If you want to say hi, I'd love to hear it! [Discussions](https://github.com/Slashee-the-Cow/CalibrationShapesReborn/discussions) is the place for you.

---

Based on [Calibration Shapes by 5@xes](https://github.com/5axes/Calibration-Shapes/) which itself was based on [Cura-SimpleShapes by fieldOfView](https://github.com/fieldOfView/Cura-SimpleShapes).  
Uses the [Trimesh](https://github.com/mikedh/trimesh) library to create [simple shapes](https://github.com/mikedh/trimesh/blob/master/trimesh/creation.py) and to load STL files.