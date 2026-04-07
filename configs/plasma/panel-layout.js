var oldPanels = panels();
for (var i = 0; i < oldPanels.length; ++i) {
  oldPanels[i].remove();
}

var panel = new Panel;
panel.location = 'top';
panel.height = 46;
try { panel.floating = true; } catch (e) {}
try { panel.alignment = 'center'; } catch (e) {}
try { panel.lengthMode = 'fit'; } catch (e) {}
try { panel.minimumLength = 900; } catch (e) {}
try { panel.maximumLength = 1400; } catch (e) {}
try { panel.offset = 0; } catch (e) {}
try { panel.hiding = 'none'; } catch (e) {}

var leftSpacer = panel.addWidget('org.kde.plasma.panelspacer');
try { leftSpacer.currentConfigGroup = ['General']; leftSpacer.writeConfig('expanding', false); } catch (e) {}
panel.addWidget('org.kde.plasma.kickoff');
panel.addWidget('org.kde.plasma.icontasks');
var centerSpacer = panel.addWidget('org.kde.plasma.panelspacer');
try { centerSpacer.currentConfigGroup = ['General']; centerSpacer.writeConfig('expanding', true); } catch (e) {}
panel.addWidget('org.kde.plasma.systemtray');
panel.addWidget('org.kde.plasma.digitalclock');
var rightSpacer = panel.addWidget('org.kde.plasma.panelspacer');
try { rightSpacer.currentConfigGroup = ['General']; rightSpacer.writeConfig('expanding', false); } catch (e) {}
