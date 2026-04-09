var oldPanels = panels();
for (var i = 0; i < oldPanels.length; ++i) {
  oldPanels[i].remove();
}
var panel = new Panel;
panel.location = 'top';
panel.height = 44;
try { panel.floating = true; } catch (e) {}
try { panel.alignment = 'center'; } catch (e) {}
try { panel.lengthMode = 'fit'; } catch (e) {}
try { panel.minimumLength = 980; } catch (e) {}
try { panel.maximumLength = 1380; } catch (e) {}
try { panel.opacityMode = 'adaptive'; } catch (e) {}
panel.addWidget('org.kde.plasma.kickoff');
panel.addWidget('org.kde.plasma.icontasks');
var spacer = panel.addWidget('org.kde.plasma.panelspacer');
try { spacer.currentConfigGroup = ['General']; spacer.writeConfig('expanding', true); } catch (e) {}
panel.addWidget('org.kde.plasma.systemtray');
panel.addWidget('org.kde.plasma.digitalclock');
