var oldPanels = panels();
for (var i = 0; i < oldPanels.length; ++i) {
  oldPanels[i].remove();
}

var panel = new Panel;
panel.location = 'top';
panel.height = 42;
try { panel.floating = true; } catch (e) {}
try { panel.alignment = 'center'; } catch (e) {}
try { panel.hiding = 'none'; } catch (e) {}

panel.addWidget('org.kde.plasma.kickoff');
panel.addWidget('org.kde.plasma.icontasks');
panel.addWidget('org.kde.plasma.systemtray');
panel.addWidget('org.kde.plasma.digitalclock');
