#!/usr/bin/env python3
"""
Dynamic Island for macOS - Clean Version
Optimized for performance with anti-spam protection
"""

try:
    from AppKit import (NSWindow, NSApplication, NSScreen, NSView, NSColor, NSBezierPath,
                        NSRect, NSPoint, NSSize, NSWindowStyleMaskBorderless,
                        NSApp, NSObject, NSMakeRect, NSEvent, NSTrackingArea, NSTrackingMouseEnteredAndExited,
                        NSTrackingActiveAlways, NSTrackingInVisibleRect, NSHapticFeedbackManager,
                        NSPointInRect, NSAnimationContext, NSTextField, NSFont, NSTextAlignmentCenter,
                        NSButton, NSBox, NSImage, NSWorkspace, NSImageView, NSSlider, NSData, NSPopUpButton,
                        NSOpenPanel, NSScrollView, NSTextView, NSURL, NSGradient, NSShadow, NSVisualEffectView)
    import objc
    import subprocess
    import time
    import threading
    import random
    import urllib.request
    import os
    from datetime import datetime, timedelta
    from PyObjCTools import AppHelper
    
    # Import macOS Media Remote Framework
    try:
        from MediaPlayer import (MPNowPlayingInfoCenter, MPMediaItemPropertyTitle,
                                MPMediaItemPropertyArtist, MPMediaItemPropertyArtwork,
                                MPNowPlayingInfoPropertyElapsedPlaybackTime,
                                MPMediaItemPropertyPlaybackDuration,
                                MPNowPlayingInfoPropertyPlaybackRate,
                                MPRemoteCommandCenter, MPRemoteCommand)
        MEDIA_FRAMEWORK_AVAILABLE = True
    except ImportError:
        MEDIA_FRAMEWORK_AVAILABLE = False
    
    class SettingsWindow(NSWindow):
        """Settings window"""

        def initWithControlPanel_(self, controlPanel):
            # Create window with proper size and style
            frame = NSMakeRect(0, 0, 900, 700)
            self = objc.super(SettingsWindow, self).initWithContentRect_styleMask_backing_defer_(
                frame,
                15,  # Titled, Closable, Miniaturizable, Resizable
                2,   # Buffered
                False
            )
            if self:
                self.parent = None
                self.setTitle_("Dynamic Island Settings")
                self.setReleasedWhenClosed_(False)

                # Center the window
                self.center()

                # Create scrollable content view
                scrollView = NSScrollView.alloc().initWithFrame_(frame)
                scrollView.setHasVerticalScroller_(True)
                scrollView.setHasHorizontalScroller_(False)
                scrollView.setAutohidesScrollers_(False)
                scrollView.setBorderType_(0)

                # Create content view with larger height for scrolling and pass control panel
                contentFrame = NSMakeRect(0, 0, frame.size.width, 900)
                contentView = SettingsView.alloc().initWithFrame_controlPanel_(contentFrame, controlPanel)
                contentView.parent = self
                scrollView.setDocumentView_(contentView)

                self.setContentView_(scrollView)

                # Immediately scroll to top
                contentView.setNeedsDisplay_(True)
                scrollView.contentView().setBoundsOrigin_(NSPoint(0, contentFrame.size.height - frame.size.height))
                scrollView.reflectScrolledClipView_(scrollView.contentView())

            return self

        def canBecomeKeyWindow(self):
            """Allow window to receive keyboard events even though app is accessory"""
            return True

        def canBecomeMainWindow(self):
            """Allow window to become main window"""
            return True
    
    class SettingsView(NSView):
        """Settings content view"""

        def initWithFrame_controlPanel_(self, frame, controlPanel):
            self = objc.super(SettingsView, self).initWithFrame_(frame)
            if self:
                self.parent = None
                self.controlPanel = controlPanel
                self.setupSettingsUI()
            return self
        
        def setupSettingsUI(self):
            # Modern dark background
            self.setWantsLayer_(True)
            self.layer().setBackgroundColor_(NSColor.colorWithRed_green_blue_alpha_(0.05, 0.05, 0.08, 1.0).CGColor())

            frame = self.frame()
            self.quickAccessApps = [None, None, None, None]

            # Header section with modern styling
            headerView = NSView.alloc().initWithFrame_(NSMakeRect(0, frame.size.height - 90, frame.size.width, 80))
            headerView.setWantsLayer_(True)
            headerView.layer().setBackgroundColor_(NSColor.colorWithRed_green_blue_alpha_(0.12, 0.12, 0.16, 0.95).CGColor())
            self.addSubview_(headerView)

            # Title
            titleLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(40, frame.size.height - 50, 500, 35))
            titleLabel.setStringValue_("⚙️ Dynamic Island Settings")
            titleLabel.setBezeled_(False)
            titleLabel.setDrawsBackground_(False)
            titleLabel.setEditable_(False)
            titleLabel.setTextColor_(NSColor.whiteColor())
            titleLabel.setFont_(NSFont.boldSystemFontOfSize_(26))
            self.addSubview_(titleLabel)

            # Subtitle
            subtitleLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(40, frame.size.height - 75, 600, 20))
            subtitleLabel.setStringValue_("Configure your quick access applications and presets")
            subtitleLabel.setBezeled_(False)
            subtitleLabel.setDrawsBackground_(False)
            subtitleLabel.setEditable_(False)
            subtitleLabel.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.7, 0.7, 0.8, 1.0))
            subtitleLabel.setFont_(NSFont.systemFontOfSize_(14))
            self.addSubview_(subtitleLabel)

            # 2x2 grid with card design - better spacing
            positions = ["🎯 Top Left", "⚡ Top Right", "🚀 Bottom Left", "💫 Bottom Right"]
            self.quickButtons = []
            startY = frame.size.height - 200  # More space from header to avoid overlap

            for i, position in enumerate(positions):
                row = i // 2
                col = i % 2
                x = 40 + (col * 420)
                y = startY - (row * 100)

                # Card container - sleeker design
                card = NSView.alloc().initWithFrame_(NSMakeRect(x, y, 400, 80))
                card.setWantsLayer_(True)
                card.layer().setBackgroundColor_(NSColor.colorWithRed_green_blue_alpha_(0.12, 0.12, 0.16, 0.9).CGColor())
                card.layer().setCornerRadius_(10)
                card.layer().setBorderWidth_(1)
                card.layer().setBorderColor_(NSColor.colorWithRed_green_blue_alpha_(0.2, 0.2, 0.25, 0.5).CGColor())
                self.addSubview_(card)

                # Position label
                label = NSTextField.alloc().initWithFrame_(NSMakeRect(15, 50, 200, 22))
                label.setStringValue_(position)
                label.setBezeled_(False)
                label.setDrawsBackground_(False)
                label.setEditable_(False)
                label.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.9, 0.9, 0.95, 1.0))
                label.setFont_(NSFont.systemFontOfSize_weight_(13, 0.3))  # Medium weight
                card.addSubview_(label)

                # App display field - clean, minimal design
                appField = NSTextField.alloc().initWithFrame_(NSMakeRect(15, 12, 240, 28))
                appField.setStringValue_("No app selected")
                appField.setBezeled_(False)
                appField.setDrawsBackground_(False)
                appField.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.5, 0.5, 0.55, 1.0))
                appField.setEditable_(False)
                appField.setFont_(NSFont.systemFontOfSize_(11))
                card.addSubview_(appField)
                setattr(self, f"quickField{i}", appField)

                # Browse button
                browseBtn = NSButton.alloc().initWithFrame_(NSMakeRect(265, 10, 120, 35))
                browseBtn.setTitle_("Browse...")
                browseBtn.setBezelStyle_(1)
                browseBtn.setTarget_(self)
                browseBtn.setAction_(objc.selector(self.browseQuickApp_, signature=b'v@:@'))
                browseBtn.setTag_(i)
                card.addSubview_(browseBtn)
                self.quickButtons.append(browseBtn)

            # Preset Configuration Section
            presetHeaderY = startY - 280
            presetHeader = NSTextField.alloc().initWithFrame_(NSMakeRect(40, presetHeaderY, 400, 30))
            presetHeader.setStringValue_("🎨 Preset Configuration")
            presetHeader.setBezeled_(False)
            presetHeader.setDrawsBackground_(False)
            presetHeader.setEditable_(False)
            presetHeader.setTextColor_(NSColor.whiteColor())
            presetHeader.setFont_(NSFont.boldSystemFontOfSize_(20))
            self.addSubview_(presetHeader)

            # Preset subtitle
            presetSubtitle = NSTextField.alloc().initWithFrame_(NSMakeRect(40, presetHeaderY - 22, 500, 18))
            presetSubtitle.setStringValue_("Configure apps that launch when you click preset buttons")
            presetSubtitle.setBezeled_(False)
            presetSubtitle.setDrawsBackground_(False)
            presetSubtitle.setEditable_(False)
            presetSubtitle.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.7, 0.7, 0.8, 1.0))
            presetSubtitle.setFont_(NSFont.systemFontOfSize_(12))
            self.addSubview_(presetSubtitle)

            # Initialize preset apps from control panel if available
            if hasattr(self.controlPanel, 'presetApps'):
                self.presetApps = self.controlPanel.presetApps
            else:
                self.presetApps = {
                    "Programming": [],
                    "Chilling": [],
                    "Debugging": [],
                    "Focus Mode": []
                }

            # Preset cards - 2x2 grid
            presets = [
                ("💻 Programming", "Programming", [(0.15, 0.18, 0.25), (0.08, 0.10, 0.15)]),
                ("🎧 Chilling", "Chilling", [(0.20, 0.15, 0.22), (0.12, 0.08, 0.14)]),
                ("🐛 Debugging", "Debugging", [(0.22, 0.14, 0.10), (0.14, 0.08, 0.05)]),
                ("🎯 Focus Mode", "Focus Mode", [(0.10, 0.20, 0.16), (0.05, 0.12, 0.10)])
            ]

            self.presetFields = {}
            presetStartY = presetHeaderY - 180  # Increased spacing to prevent overlap

            for i, (displayName, presetKey, gradientColors) in enumerate(presets):
                row = i // 2
                col = i % 2
                x = 40 + (col * 420)
                y = presetStartY - (row * 140)

                # Card container
                card = NSView.alloc().initWithFrame_(NSMakeRect(x, y, 400, 120))
                card.setWantsLayer_(True)
                avgR = (gradientColors[0][0] + gradientColors[1][0]) / 2
                avgG = (gradientColors[0][1] + gradientColors[1][1]) / 2
                avgB = (gradientColors[0][2] + gradientColors[1][2]) / 2
                card.layer().setBackgroundColor_(NSColor.colorWithRed_green_blue_alpha_(avgR, avgG, avgB, 0.5).CGColor())
                card.layer().setCornerRadius_(10)
                card.layer().setBorderWidth_(1)
                card.layer().setBorderColor_(NSColor.colorWithRed_green_blue_alpha_(avgR + 0.1, avgG + 0.1, avgB + 0.1, 0.5).CGColor())
                self.addSubview_(card)

                # Preset name label
                nameLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(15, 90, 200, 22))
                nameLabel.setStringValue_(displayName)
                nameLabel.setBezeled_(False)
                nameLabel.setDrawsBackground_(False)
                nameLabel.setEditable_(False)
                nameLabel.setTextColor_(NSColor.whiteColor())
                nameLabel.setFont_(NSFont.boldSystemFontOfSize_(14))
                card.addSubview_(nameLabel)

                # Apps list display (scrollable text view)
                scrollView = NSScrollView.alloc().initWithFrame_(NSMakeRect(15, 35, 370, 50))
                scrollView.setHasVerticalScroller_(True)
                scrollView.setHasHorizontalScroller_(False)
                scrollView.setAutohidesScrollers_(True)
                scrollView.setBorderType_(2)  # Bezel border for better appearance
                scrollView.setWantsLayer_(True)
                scrollView.layer().setCornerRadius_(6)
                scrollView.layer().setBorderWidth_(0.5)
                scrollView.layer().setBorderColor_(NSColor.colorWithRed_green_blue_alpha_(0.3, 0.3, 0.35, 0.6).CGColor())

                textView = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 360, 50))
                textView.setEditable_(False)
                textView.setSelectable_(True)
                textView.setBackgroundColor_(NSColor.colorWithRed_green_blue_alpha_(0.12, 0.12, 0.16, 0.9))
                textView.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.95, 0.95, 1.0, 1.0))
                textView.setFont_(NSFont.systemFontOfSize_(12))

                # Set initial text
                apps = self.presetApps.get(presetKey, [])
                if apps:
                    appNames = [os.path.basename(app).replace(".app", "") for app in apps]
                    textView.setString_(", ".join(appNames))
                else:
                    textView.setString_("No apps configured")
                    textView.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.6, 0.6, 0.65, 1.0))

                scrollView.setDocumentView_(textView)
                card.addSubview_(scrollView)
                self.presetFields[presetKey] = textView

                # Add App button
                addBtn = NSButton.alloc().initWithFrame_(NSMakeRect(15, 5, 180, 25))
                addBtn.setTitle_("Add App...")
                addBtn.setBezelStyle_(1)
                addBtn.setFont_(NSFont.systemFontOfSize_(11))
                addBtn.setTarget_(self)
                addBtn.setAction_(objc.selector(self.addPresetApp_, signature=b'v@:@'))
                addBtn.setTag_(i)  # Use index to identify which preset
                card.addSubview_(addBtn)

                # Clear All button
                clearBtn = NSButton.alloc().initWithFrame_(NSMakeRect(205, 5, 180, 25))
                clearBtn.setTitle_("Clear All")
                clearBtn.setBezelStyle_(1)
                clearBtn.setFont_(NSFont.systemFontOfSize_(11))
                clearBtn.setTarget_(self)
                clearBtn.setAction_(objc.selector(self.clearPresetApps_, signature=b'v@:@'))
                clearBtn.setTag_(i)  # Use index to identify which preset
                card.addSubview_(clearBtn)

            # Close and Quit buttons at bottom
            closeBtn = NSButton.alloc().initWithFrame_(NSMakeRect(frame.size.width/2 - 170, 30, 150, 40))
            closeBtn.setTitle_("Close")
            closeBtn.setBezelStyle_(1)
            closeBtn.setTarget_(self)
            closeBtn.setAction_(objc.selector(self.closeSettings_, signature=b'v@:@'))
            self.addSubview_(closeBtn)

            # Quit App button
            quitBtn = NSButton.alloc().initWithFrame_(NSMakeRect(frame.size.width/2 + 20, 30, 150, 40))
            quitBtn.setTitle_("Quit App")
            quitBtn.setBezelStyle_(1)
            quitBtn.setTarget_(self)
            quitBtn.setAction_(objc.selector(self.quitApp_, signature=b'v@:@'))
            # Style as a destructive action with red text
            quitBtn.setContentTintColor_(NSColor.systemRedColor())
            self.addSubview_(quitBtn)

        def browseQuickApp_(self, sender):
            """Handle browse button click to select an app"""
            index = sender.tag()
            print(f"Browse clicked for slot {index}")

            panel = NSOpenPanel.openPanel()
            panel.setCanChooseFiles_(True)
            panel.setCanChooseDirectories_(False)
            panel.setAllowsMultipleSelection_(False)
            panel.setDirectoryURL_(NSURL.fileURLWithPath_("/Applications"))
            panel.setAllowedFileTypes_(["app"])

            result = panel.runModal()
            print(f"Panel result: {result}")

            if result == 1:  # NSModalResponseOK
                url = panel.URL()
                if url:
                    appPath = url.path()
                    appName = os.path.basename(appPath).replace(".app", "")
                    print(f"Selected app: {appName} at {appPath}")

                    self.quickAccessApps[index] = appPath
                    field = getattr(self, f"quickField{index}")
                    field.setStringValue_(appName)
                    field.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.95, 0.95, 1.0, 1.0))
                    field.setFont_(NSFont.systemFontOfSize_weight_(12, 0.2))  # Slightly larger and medium weight
                    print(f"Updated field {index} to: {appName}")

                    # Update the control panel's quick access button
                    if hasattr(self, 'controlPanel') and self.controlPanel:
                        print(f"Updating control panel button {index} with app: {appPath}")
                        self.controlPanel.updateQuickAccessButton_withPath_(index, appPath)

        def addPresetApp_(self, sender):
            """Handle Add App button click for presets"""
            index = sender.tag()
            presets = ["Programming", "Chilling", "Debugging", "Focus Mode"]
            presetKey = presets[index]

            print(f"Add app clicked for preset: {presetKey}")

            panel = NSOpenPanel.openPanel()
            panel.setCanChooseFiles_(True)
            panel.setCanChooseDirectories_(False)
            panel.setAllowsMultipleSelection_(False)
            panel.setDirectoryURL_(NSURL.fileURLWithPath_("/Applications"))
            panel.setAllowedFileTypes_(["app"])

            result = panel.runModal()

            if result == 1:  # NSModalResponseOK
                url = panel.URL()
                if url:
                    appPath = url.path()
                    appName = os.path.basename(appPath).replace(".app", "")
                    print(f"Selected app for {presetKey}: {appName} at {appPath}")

                    # Add to preset apps
                    if presetKey not in self.presetApps:
                        self.presetApps[presetKey] = []

                    if appPath not in self.presetApps[presetKey]:
                        self.presetApps[presetKey].append(appPath)

                        # Update display
                        self.updatePresetDisplay_(presetKey)

                        # Update control panel
                        if hasattr(self, 'controlPanel') and self.controlPanel:
                            self.controlPanel.presetApps = self.presetApps
                            self.controlPanel.saveSettings()
                            print(f"Updated control panel with new preset apps")

        def clearPresetApps_(self, sender):
            """Handle Clear All button click for presets"""
            index = sender.tag()
            presets = ["Programming", "Chilling", "Debugging", "Focus Mode"]
            presetKey = presets[index]

            print(f"Clear all clicked for preset: {presetKey}")

            # Clear preset apps
            self.presetApps[presetKey] = []

            # Update display
            self.updatePresetDisplay_(presetKey)

            # Update control panel
            if hasattr(self, 'controlPanel') and self.controlPanel:
                self.controlPanel.presetApps = self.presetApps
                self.controlPanel.saveSettings()
                print(f"Cleared all apps for {presetKey}")

        def updatePresetDisplay_(self, presetKey):
            """Update the text view showing apps for a preset"""
            textView = self.presetFields.get(presetKey)
            if textView:
                apps = self.presetApps.get(presetKey, [])
                if apps:
                    appNames = [os.path.basename(app).replace(".app", "") for app in apps]
                    textView.setString_(", ".join(appNames))
                    textView.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.95, 0.95, 1.0, 1.0))
                else:
                    textView.setString_("No apps configured")
                    textView.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.6, 0.6, 0.65, 1.0))

        def closeSettings_(self, sender):
            """Close the settings window"""
            window = self.window()
            if window:
                window.close()

        def quitApp_(self, sender):
            """Quit the entire application"""
            NSApplication.sharedApplication().terminate_(None)

    class ControlPanelView(NSView):
        """Main control panel with buttons"""
        
        def initWithFrame_(self, frame):
            self = objc.super(ControlPanelView, self).initWithFrame_(frame)
            if self:
                self.lastClickTime = {}  # Anti-spam tracking
                self.lastVolumeSliderTouch = 0  # Track when user last touched volume slider
                self.lastProgressSliderTouch = 0  # Track when user last touched progress slider
                self.lastSeekCommandTime = 0  # Track actual seek command execution
                self.lastVolumeCommandTime = 0  # Track actual volume command execution
                self.pendingSeekValue = None  # Store pending seek value
                self.pendingVolumeValue = None  # Store pending volume value
                self.setupControls()
            return self
        
        def setupControls(self):
            # Quick Access section - moved left 30px
            quickAccessLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(25, 93, 80, 18))
            quickAccessLabel.setStringValue_("Quick Access")
            quickAccessLabel.setBezeled_(False)
            quickAccessLabel.setDrawsBackground_(False)
            quickAccessLabel.setEditable_(False)
            quickAccessLabel.setTextColor_(NSColor.lightGrayColor())
            quickAccessLabel.setFont_(NSFont.systemFontOfSize_(11))
            quickAccessLabel.setAlignment_(NSTextAlignmentCenter)
            self.addSubview_(quickAccessLabel)
            
            # 2x2 Grid with app icons - moved left 30px with Quick Access
            gridX = 25  # Moved left 30px
            gridY = 13  # Moved down 4px more
            iconSize = 40
            spacing = 45
            
            # Load settings from persistent storage
            self.loadSettings()

            # Initialize empty if no settings loaded
            if not hasattr(self, 'quickAppPaths') or not self.quickAppPaths:
                self.quickAppPaths = [None, None, None, None]
            
            # Create Quick Access buttons
            self.quickButtons = []
            actions = [self.launchQuickApp0_, self.launchQuickApp1_, self.launchQuickApp2_, self.launchQuickApp3_]
            positions = [
                (gridX, gridY + spacing),  # Top-left
                (gridX + spacing, gridY + spacing),  # Top-right
                (gridX, gridY),  # Bottom-left
                (gridX + spacing, gridY)  # Bottom-right
            ]

            for i in range(4):
                x, y = positions[i]
                if self.quickAppPaths[i]:
                    btn = self.createAppIconButton_x_y_action_(self.quickAppPaths[i], x, y, actions[i])
                else:
                    btn = self.createEmptyQuickAccessButtonAtX_y_index_(x, y, i)
                self.quickButtons.append(btn)
            
            # Plus sign divider to separate the 4 icons - FULL OPACITY
            # Horizontal line of the plus
            horizontalDivider = NSBox.alloc().initWithFrame_(NSMakeRect(gridX - 5, gridY + 20 + spacing/2, spacing + iconSize + 10, 3))
            horizontalDivider.setBoxType_(2)
            horizontalDivider.setFillColor_(NSColor.grayColor())
            horizontalDivider.setAlphaValue_(1.0)  # MAX OPACITY
            self.addSubview_(horizontalDivider)
            
            # Vertical line of the plus - moved left 3px
            verticalDivider = NSBox.alloc().initWithFrame_(NSMakeRect(gridX + 17 + spacing/2, gridY - 5, 3, spacing + iconSize + 10))
            verticalDivider.setBoxType_(2)
            verticalDivider.setFillColor_(NSColor.grayColor())
            verticalDivider.setAlphaValue_(1.0)  # MAX OPACITY
            self.addSubview_(verticalDivider)
            
            
            # First divider (vertical) - moved right 5px and up 5px
            divider1 = NSBox.alloc().initWithFrame_(NSMakeRect(125, 5, 1, 100))
            divider1.setBoxType_(2)  # NSBoxSeparator
            divider1.setBorderColor_(NSColor.darkGrayColor())
            self.addSubview_(divider1)
            
            # Setup buttons (vertical stack aligned with Quick Access) - moved up 30px with gradients
            self.programmingBtn = self.createSetupButton_x_y_action_gradient_("Programming", 130, 95, self.setupProgramming_,
                [(0.15, 0.18, 0.25), (0.08, 0.10, 0.15)])  # Deep blue-ish gradient
            self.chillingBtn = self.createSetupButton_x_y_action_gradient_("Chilling", 130, 70, self.setupChilling_,
                [(0.20, 0.15, 0.22), (0.12, 0.08, 0.14)])  # Deep purple gradient
            self.debuggingBtn = self.createSetupButton_x_y_action_gradient_("Debugging", 130, 45, self.setupDebugging_,
                [(0.22, 0.14, 0.10), (0.14, 0.08, 0.05)])  # Deep orange/rust gradient
            self.focusBtn = self.createSetupButton_x_y_action_gradient_("Focus Mode", 130, 20, self.setupFocus_,
                [(0.10, 0.20, 0.16), (0.05, 0.12, 0.10)])  # Deep teal/green gradient
            
            # Presets subtitle - moved left 8px
            presetsLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(155, 1, 60, 15))
            presetsLabel.setStringValue_("Presets")
            presetsLabel.setBezeled_(False)
            presetsLabel.setDrawsBackground_(False)
            presetsLabel.setEditable_(False)
            presetsLabel.setTextColor_(NSColor.lightGrayColor())
            presetsLabel.setFont_(NSFont.systemFontOfSize_(10))
            presetsLabel.setAlignment_(NSTextAlignmentCenter)
            self.addSubview_(presetsLabel)
            
            # Second divider (vertical) - moved left 8px more
            divider2 = NSBox.alloc().initWithFrame_(NSMakeRect(256, 10, 1, 70))
            divider2.setBoxType_(2)
            divider2.setBorderColor_(NSColor.darkGrayColor())
            self.addSubview_(divider2)
            
            # Date/Time Section (in the center)
            self.setupDateTime()
            
            # Third divider (vertical) - left of media player, same as divider2
            divider3 = NSBox.alloc().initWithFrame_(NSMakeRect(440, 10, 1, 70))
            divider3.setBoxType_(2)
            divider3.setBorderColor_(NSColor.darkGrayColor())
            self.addSubview_(divider3)
            
            # Media Player Section (in the middle)
            self.setupMediaPlayer()
        
        def setupMediaPlayer(self):
            """Setup media player controls in the right section"""
            # Album art / placeholder - moved to right section - moved left 75px total, down 5px
            self.albumArt = NSImageView.alloc().initWithFrame_(NSMakeRect(455, 60, 50, 50))
            self.albumArt.setImageScaling_(2)  # Proportionally up or down
            
            # Set placeholder gray album art
            placeholderImage = NSImage.alloc().initWithSize_(NSSize(50, 50))
            placeholderImage.lockFocus()
            NSColor.darkGrayColor().set()
            NSBezierPath.fillRect_(NSMakeRect(0, 0, 50, 50))
            placeholderImage.unlockFocus()
            self.albumArt.setImage_(placeholderImage)
            self.addSubview_(self.albumArt)
            
            # Song title - next to album art (2 lines for overflow) - moved down 5px
            self.songTitle = NSTextField.alloc().initWithFrame_(NSMakeRect(511, 83, 159, 26))
            self.songTitle.setStringValue_("Locked In")
            self.songTitle.setBezeled_(False)
            self.songTitle.setDrawsBackground_(False)
            self.songTitle.setEditable_(False)
            self.songTitle.setTextColor_(NSColor.whiteColor())
            self.songTitle.setFont_(NSFont.boldSystemFontOfSize_(9))
            self.songTitle.setMaximumNumberOfLines_(2)
            self.songTitle.setLineBreakMode_(0)  # Word wrap
            self.addSubview_(self.songTitle)
            
            # Artist name - moved down 5px
            self.artistName = NSTextField.alloc().initWithFrame_(NSMakeRect(511, 81, 159, 16))
            self.artistName.setStringValue_("")
            self.artistName.setBezeled_(False)
            self.artistName.setDrawsBackground_(False)
            self.artistName.setEditable_(False)
            self.artistName.setTextColor_(NSColor.lightGrayColor())  # Keep artist name light gray
            self.artistName.setFont_(NSFont.boldSystemFontOfSize_(11))  # 2pt smaller than before
            self.artistName.setMaximumNumberOfLines_(1)  # Force single line
            self.artistName.setLineBreakMode_(2)  # Truncate tail if too long
            self.addSubview_(self.artistName)
            
            # Progress slider - iOS-style pill with circular knob
            pillHeight = 8  # Pill track height
            frameHeight = 10  # Frame height for the slider bar
            knobThickness = 4  # Actual circular knob size
            self.progressSlider = NSSlider.alloc().initWithFrame_(NSMakeRect(452, 39, 218, frameHeight))
            self.progressSlider.setMinValue_(0)
            self.progressSlider.setMaxValue_(100)
            self.progressSlider.setDoubleValue_(0)
            self.progressSlider.setContinuous_(True)  # Fire events continuously while dragging
            self.progressSlider.setTarget_(self)
            self.progressSlider.setAction_(objc.selector(self.seekTrack_, signature=b'v@:@'))
            self.progressSlider.setWantsLayer_(True)

            # Create custom circular knob that fits inside the pill
            sliderCell = self.progressSlider.cell()
            if sliderCell:
                sliderCell.setControlSize_(2)  # Small control size
                sliderCell.setSliderType_(0)  # Linear
                # Circular knob
                sliderCell.setKnobThickness_(knobThickness)

            # Style the track as a pill - hollow with border
            self.progressSlider.layer().setCornerRadius_(pillHeight / 2)
            self.progressSlider.layer().setMasksToBounds_(False)
            # Add a border to make it look like a hollow pill
            self.progressSlider.layer().setBorderWidth_(1.5)
            self.progressSlider.layer().setBorderColor_(NSColor.colorWithRed_green_blue_alpha_(0.4, 0.4, 0.45, 0.8).CGColor())
            self.progressSlider.layer().setBackgroundColor_(NSColor.clearColor().CGColor())  # Transparent background

            self.addSubview_(self.progressSlider)
            
            # Volume slider - iOS-style pill with circular knob
            volumePillHeight = 8  # Pill track height
            volumeFrameHeight = 10  # Frame height for the slider bar
            volumeKnobThickness = 4  # Actual circular knob size
            self.volumeSlider = NSSlider.alloc().initWithFrame_(NSMakeRect(583, 55, 87, volumeFrameHeight))
            self.volumeSlider.setMinValue_(0)
            self.volumeSlider.setMaxValue_(100)
            self.volumeSlider.setDoubleValue_(50)  # Default to 50% volume
            self.volumeSlider.setContinuous_(True)  # Fire events continuously while dragging
            self.volumeSlider.setTarget_(self)
            self.volumeSlider.setAction_(objc.selector(self.changeVolume_, signature=b'v@:@'))
            self.volumeSlider.setWantsLayer_(True)

            # Create custom circular knob that fits inside the pill
            volumeCell = self.volumeSlider.cell()
            if volumeCell:
                volumeCell.setControlSize_(2)  # Small control size
                volumeCell.setSliderType_(0)  # Linear
                # Circular knob
                volumeCell.setKnobThickness_(volumeKnobThickness)

            # Style the track as a pill - hollow with border
            self.volumeSlider.layer().setCornerRadius_(volumePillHeight / 2)
            self.volumeSlider.layer().setMasksToBounds_(False)
            # Add a border to make it look like a hollow pill
            self.volumeSlider.layer().setBorderWidth_(1.5)
            self.volumeSlider.layer().setBorderColor_(NSColor.colorWithRed_green_blue_alpha_(0.4, 0.4, 0.45, 0.8).CGColor())
            self.volumeSlider.layer().setBackgroundColor_(NSColor.clearColor().CGColor())  # Transparent background

            self.addSubview_(self.volumeSlider)
            
            # Media control buttons - under the slider
            # Previous button - double triangles - moved right 10px, down 5px
            self.prevBtn = NSButton.alloc().initWithFrame_(NSMakeRect(509, 15, 30, 20))
            self.prevBtn.setTitle_("◀◀")
            self.prevBtn.setBezelStyle_(0)
            self.prevBtn.setBordered_(False)
            self.prevBtn.setFont_(NSFont.systemFontOfSize_(12))
            self.prevBtn.setTarget_(self)
            self.prevBtn.setAction_(objc.selector(self.previousTrack_, signature=b'v@:@'))
            self.addSubview_(self.prevBtn)
            
            # Play/Pause button - 15% bigger and moved right 10px, down 5px
            self.playBtn = NSButton.alloc().initWithFrame_(NSMakeRect(539, 11, 41, 28))  # 15% bigger
            self.playBtn.setTitle_("▶")  # Simple triangle
            self.playBtn.setBezelStyle_(0)
            self.playBtn.setBordered_(False)
            self.playBtn.setFont_(NSFont.systemFontOfSize_(18))  # Larger font too
            self.playBtn.setTarget_(self)
            self.playBtn.setAction_(objc.selector(self.playPause_, signature=b'v@:@'))
            self.addSubview_(self.playBtn)
            
            # Next button - double triangles - moved right 10px, down 5px
            self.nextBtn = NSButton.alloc().initWithFrame_(NSMakeRect(579, 15, 30, 20))
            self.nextBtn.setTitle_("▶▶")
            self.nextBtn.setBezelStyle_(0)
            self.nextBtn.setBordered_(False)
            self.nextBtn.setFont_(NSFont.systemFontOfSize_(12))
            self.nextBtn.setTarget_(self)
            self.nextBtn.setAction_(objc.selector(self.nextTrack_, signature=b'v@:@'))
            self.addSubview_(self.nextBtn)
            
            # Start updating media info
            self.updateMediaInfo()
        
        def setupDateTime(self):
            """Setup date and time display in the center"""
            now = datetime.now()
            yesterday = now - timedelta(days=1)
            tomorrow = now + timedelta(days=1)
            
            # Center X position for the date/time section
            centerX = 348  # Center between dividers (256 and 440)
            
            # Today's date (big number in center) - lowered 7px
            self.todayDate = NSTextField.alloc().initWithFrame_(NSMakeRect(centerX - 20, 48, 40, 35))
            self.todayDate.setStringValue_(str(int(now.strftime("%d"))))  # Remove leading zero
            self.todayDate.setBezeled_(False)
            self.todayDate.setDrawsBackground_(False)
            self.todayDate.setEditable_(False)
            self.todayDate.setTextColor_(NSColor.whiteColor())
            self.todayDate.setFont_(NSFont.boldSystemFontOfSize_(28))
            self.todayDate.setAlignment_(NSTextAlignmentCenter)
            self.addSubview_(self.todayDate)
            
            # Yesterday's date (small, left and up) - raised 3px more
            self.yesterdayDate = NSTextField.alloc().initWithFrame_(NSMakeRect(centerX - 50, 66, 25, 15))
            self.yesterdayDate.setStringValue_(str(int(yesterday.strftime("%d"))))  # Remove leading zero
            self.yesterdayDate.setBezeled_(False)
            self.yesterdayDate.setDrawsBackground_(False)
            self.yesterdayDate.setEditable_(False)
            self.yesterdayDate.setTextColor_(NSColor.grayColor())
            self.yesterdayDate.setFont_(NSFont.systemFontOfSize_(10))
            self.yesterdayDate.setAlignment_(NSTextAlignmentCenter)
            self.addSubview_(self.yesterdayDate)
            
            # Tomorrow's date (small, right and up) - raised 3px more
            self.tomorrowDate = NSTextField.alloc().initWithFrame_(NSMakeRect(centerX + 25, 66, 25, 15))
            self.tomorrowDate.setStringValue_(str(int(tomorrow.strftime("%d"))))  # Remove leading zero
            self.tomorrowDate.setBezeled_(False)
            self.tomorrowDate.setDrawsBackground_(False)
            self.tomorrowDate.setEditable_(False)
            self.tomorrowDate.setTextColor_(NSColor.grayColor())
            self.tomorrowDate.setFont_(NSFont.systemFontOfSize_(10))
            self.tomorrowDate.setAlignment_(NSTextAlignmentCenter)
            self.addSubview_(self.tomorrowDate)
            
            # Time in 12-hour format (under the date) - lowered 7px
            self.timeLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(centerX - 30, 28, 60, 18))
            self.timeLabel.setStringValue_(now.strftime("%I:%M"))
            self.timeLabel.setBezeled_(False)
            self.timeLabel.setDrawsBackground_(False)
            self.timeLabel.setEditable_(False)
            self.timeLabel.setTextColor_(NSColor.whiteColor())
            self.timeLabel.setFont_(NSFont.systemFontOfSize_(14))
            self.timeLabel.setAlignment_(NSTextAlignmentCenter)
            self.addSubview_(self.timeLabel)
            
            # Day of the week (under the time) - lowered 7px
            self.dayLabel = NSTextField.alloc().initWithFrame_(NSMakeRect(centerX - 35, 11, 70, 16))
            self.dayLabel.setStringValue_(now.strftime("%A"))
            self.dayLabel.setBezeled_(False)
            self.dayLabel.setDrawsBackground_(False)
            self.dayLabel.setEditable_(False)
            self.dayLabel.setTextColor_(NSColor.lightGrayColor())
            self.dayLabel.setFont_(NSFont.systemFontOfSize_(11))
            self.dayLabel.setAlignment_(NSTextAlignmentCenter)
            self.addSubview_(self.dayLabel)
            
            # Settings gear button (bottom right of calendar section)
            self.settingsBtn = NSButton.alloc().initWithFrame_(NSMakeRect(centerX + 60, 5, 28, 28))
            self.settingsBtn.setTitle_("⚙")
            self.settingsBtn.setBezelStyle_(0)
            self.settingsBtn.setBordered_(False)
            self.settingsBtn.setFont_(NSFont.systemFontOfSize_(18))
            self.settingsBtn.setTarget_(self)
            self.settingsBtn.setAction_(objc.selector(self.showSettings_, signature=b'v@:@'))
            self.addSubview_(self.settingsBtn)
            
            # Start updating time
            self.updateDateTime()
            
            # Initialize settings window (hidden by default)
            self.settingsWindow = None
        

        def showSettings_(self, sender):
            """Toggle settings window"""
            print("DEBUG: showSettings_ called")
            print(f"DEBUG: Has settingsWindow: {hasattr(self, 'settingsWindow')}")
            if hasattr(self, 'settingsWindow'):
                print(f"DEBUG: settingsWindow exists: {self.settingsWindow}")
                if self.settingsWindow:
                    print(f"DEBUG: isVisible: {self.settingsWindow.isVisible()}")

            if hasattr(self, 'settingsWindow') and self.settingsWindow and self.settingsWindow.isVisible():
                print("DEBUG: Closing existing settings window")
                # Hide settings and revert policy
                if hasattr(self.settingsWindow, 'revertPolicy'):
                    self.settingsWindow.revertPolicy()
                self.settingsWindow.close()
                self.settingsWindow = None
            else:
                print("DEBUG: Calling showSettingsWindow")
                # Show settings
                self.showSettingsWindow()
        
        def showSettingsWindow(self):
            """Create and display settings window"""
            print("DEBUG: showSettingsWindow called")
            try:
                # Create settings window and pass control panel reference
                print("DEBUG: Creating SettingsWindow")
                self.settingsWindow = SettingsWindow.alloc().initWithControlPanel_(self)
                print(f"DEBUG: SettingsWindow created: {self.settingsWindow}")

                # Show the window - canBecomeKeyWindow allows it to receive events
                # even though the app is an accessory (LSUIElement=true)
                print("DEBUG: Making window key and ordering front")
                self.settingsWindow.makeKeyAndOrderFront_(None)

                print("DEBUG: Settings window should now be visible and interactive")
            except Exception as e:
                print(f"DEBUG: ERROR in showSettingsWindow: {e}")
                import traceback
                traceback.print_exc()
        
        def updateDateTime(self):
            """Update date and time display"""
            def update():
                now = datetime.now()
                yesterday = now - timedelta(days=1)
                tomorrow = now + timedelta(days=1)
                
                self.todayDate.setStringValue_(str(int(now.strftime("%d"))))
                self.yesterdayDate.setStringValue_(str(int(yesterday.strftime("%d"))))
                self.tomorrowDate.setStringValue_(str(int(tomorrow.strftime("%d"))))
                self.timeLabel.setStringValue_(now.strftime("%I:%M"))
                self.dayLabel.setStringValue_(now.strftime("%A"))
                
                # Schedule next update in 60 seconds
                threading.Timer(60.0, self.updateDateTime).start()
            
            threading.Thread(target=update).start()
        
        def updateMediaInfo(self):
            """Update media info from system Now Playing"""
            def update():
                print("[DEBUG] update() called", flush=True)
                try:
                    # Update volume slider to current system volume (only if not recently touched)
                    volume_script = 'output volume of (get volume settings)'
                    volume_result = subprocess.run(['osascript', '-e', volume_script], capture_output=True, text=True)
                    if volume_result.stdout.strip():
                        try:
                            current_volume = int(volume_result.stdout.strip())
                            # Only update if user hasn't touched slider in last 5 seconds
                            if time.time() - self.lastVolumeSliderTouch > 5.0:
                                self.volumeSlider.setDoubleValue_(current_volume)
                        except:
                            pass
                    if MEDIA_FRAMEWORK_AVAILABLE:
                        # Get system-wide now playing info
                        infoCenter = MPNowPlayingInfoCenter.defaultCenter()
                        nowPlaying = infoCenter.nowPlayingInfo()
                        print(f"[DEBUG] nowPlaying: {nowPlaying is not None}", flush=True)

                        if nowPlaying:
                            # Get track info
                            title = nowPlaying.get(MPMediaItemPropertyTitle, "")
                            artist = nowPlaying.get(MPMediaItemPropertyArtist, "")
                            playbackRate = nowPlaying.get(MPNowPlayingInfoPropertyPlaybackRate, 0)
                            elapsed = nowPlaying.get(MPNowPlayingInfoPropertyElapsedPlaybackTime, 0)
                            duration = nowPlaying.get(MPMediaItemPropertyPlaybackDuration, 0)
                            print(f"[DEBUG] title: '{title}'", flush=True)

                            if title:
                                self.songTitle.setStringValue_(title)
                                
                                # Check if title wraps to multiple lines and adjust artist position
                                # Move down 8px for every 20 characters
                                lines = (len(title) // 20) + (1 if len(title) % 20 > 0 else 0)
                                artistFrame = self.artistName.frame()
                                artistFrame.origin.y = 81 - (8 * (lines - 1))  # Base position minus 8px per extra line
                                self.artistName.setFrame_(artistFrame)
                                
                                self.artistName.setStringValue_(artist[:15] if artist else "")
                                
                                # Update play/pause button
                                if playbackRate > 0:
                                    self.playBtn.setTitle_("❚❚")
                                else:
                                    self.playBtn.setTitle_("▶")
                                
                                # Update progress slider (only if not recently touched)
                                if duration > 0:
                                    percentage = (elapsed / duration) * 100
                                    # Only update if user hasn't touched slider in last 5 seconds
                                    if time.time() - self.lastProgressSliderTouch > 5.0:
                                        self.progressSlider.setDoubleValue_(percentage)
                                
                                # Get album artwork if available
                                artwork = nowPlaying.get(MPMediaItemPropertyArtwork)
                                print(f"[ART] nowPlaying artwork: {artwork}", flush=True)
                                if artwork:
                                    image = artwork.imageWithSize_(NSSize(60, 60))
                                    print(f"[ART] Got image from nowPlaying: {image}")
                                    if image:
                                        self.albumArt.setImage_(image)
                                        print(f"[ART] Set image from nowPlaying")
                                else:
                                    # No artwork from nowPlayingCenter - try Spotify AppleScript
                                    print("[ART] No artwork from nowPlayingCenter, trying Spotify...")
                                    try:
                                        result = subprocess.run(['osascript', '-e',
                                            'tell application "Spotify" to return artwork url of current track'],
                                            capture_output=True, text=True, timeout=0.5)
                                        artworkUrl = result.stdout.strip()
                                        print(f"[ART] Spotify artwork URL: '{artworkUrl}'")
                                        if artworkUrl and artworkUrl.startswith('http'):
                                            print(f"[ART] URL valid, checking cache...")
                                            # Cache check
                                            if not hasattr(self, 'lastArtworkUrl') or self.lastArtworkUrl != artworkUrl:
                                                self.lastArtworkUrl = artworkUrl
                                                print(f"[ART] Starting download thread...")
                                                def downloadArtwork():
                                                    try:
                                                        print(f"[ART] Downloading from {artworkUrl}")
                                                        with urllib.request.urlopen(artworkUrl, timeout=3) as response:
                                                            imageBytes = response.read()
                                                            print(f"[ART] Downloaded {len(imageBytes)} bytes")
                                                            imageData = NSData.dataWithBytes_length_(imageBytes, len(imageBytes))
                                                            image = NSImage.alloc().initWithData_(imageData)
                                                            if image:
                                                                print(f"[ART] Created NSImage, setting to albumArt view")
                                                                self.albumArt.setImage_(image)
                                                                print(f"[ART] Done!")
                                                            else:
                                                                print(f"[ART] Failed to create NSImage")
                                                    except Exception as e:
                                                        print(f"[ART] Download error: {e}")
                                                threading.Thread(target=downloadArtwork, daemon=True).start()
                                            else:
                                                print(f"[ART] Using cached (same URL)")
                                        else:
                                            print(f"[ART] URL invalid or empty")
                                    except Exception as e:
                                        print(f"[ART] Spotify error: {e}")
                            else:
                                self.songTitle.setStringValue_("Locked In")
                                # Reset artist position for default text
                                artistFrame = self.artistName.frame()
                                artistFrame.origin.y = 86
                                self.artistName.setFrame_(artistFrame)
                                self.artistName.setStringValue_("")
                                self.playBtn.setTitle_("▶")
                        else:
                            # Fall back to AppleScript for Spotify
                            script = '''
                            tell application "System Events"
                                if exists process "Spotify" then
                                    tell application "Spotify"
                                        set playerState to player state as string
                                        if playerState is "playing" or playerState is "paused" then
                                            return name of current track & "|" & artist of current track & "|" & player position & "|" & (duration of current track / 1000) & "|" & playerState & "|" & artwork url of current track
                                        else
                                            return "stopped"
                                        end if
                                    end tell
                                else
                                    return "not_running"
                                end if
                            end tell
                            '''
                            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)

                            if result.stdout.strip() not in ["stopped", "not_running", ""]:
                                info = result.stdout.strip().split("|")
                                if len(info) >= 2:
                                    self.songTitle.setStringValue_(info[0])
                                    
                                    # Check if title wraps to multiple lines and adjust artist position
                                    # Move down 8px for every 20 characters
                                    lines = (len(info[0]) // 20) + (1 if len(info[0]) % 20 > 0 else 0)
                                    artistFrame = self.artistName.frame()
                                    artistFrame.origin.y = 81 - (8 * (lines - 1))  # Base position minus 8px per extra line
                                    self.artistName.setFrame_(artistFrame)
                                    
                                    self.artistName.setStringValue_(info[1][:15])
                                    
                                    if len(info) >= 5:
                                        if "paused" in info[4]:
                                            self.playBtn.setTitle_("▶")
                                        else:
                                            self.playBtn.setTitle_("❚❚")
                                    
                                    if len(info) >= 4:
                                        try:
                                            position = float(info[2])
                                            duration = float(info[3])
                                            if duration > 0:
                                                percentage = (position / duration) * 100
                                                # Only update if user hasn't touched slider in last 5 seconds
                                                if time.time() - self.lastProgressSliderTouch > 5.0:
                                                    self.progressSlider.setDoubleValue_(percentage)
                                        except:
                                            pass

                                    # Download album artwork if available
                                    if len(info) >= 6 and info[5]:
                                        artworkUrl = info[5].strip()
                                        # Cache check - don't redownload same artwork
                                        if not hasattr(self, 'lastArtworkUrl') or self.lastArtworkUrl != artworkUrl:
                                            self.lastArtworkUrl = artworkUrl
                                            # Download in background thread to avoid blocking UI
                                            def downloadArtwork():
                                                try:
                                                    with urllib.request.urlopen(artworkUrl, timeout=3) as response:
                                                        imageBytes = response.read()
                                                        imageData = NSData.dataWithBytes_length_(imageBytes, len(imageBytes))
                                                        image = NSImage.alloc().initWithData_(imageData)
                                                        if image:
                                                            self.albumArt.setImage_(image)
                                                except:
                                                    pass
                                            threading.Thread(target=downloadArtwork, daemon=True).start()
                            else:
                                self.songTitle.setStringValue_("Locked In")
                                # Reset artist position for default text
                                artistFrame = self.artistName.frame()
                                artistFrame.origin.y = 86
                                self.artistName.setFrame_(artistFrame)
                                self.artistName.setStringValue_("")
                                self.playBtn.setTitle_("▶")
                    else:
                        # Original AppleScript fallback
                        script = '''
                        tell application "System Events"
                            if exists process "Spotify" then
                                tell application "Spotify"
                                    set playerState to player state as string
                                    if playerState is "playing" or playerState is "paused" then
                                        return name of current track & "|" & artist of current track & "|" & player position & "|" & (duration of current track / 1000) & "|" & playerState
                                    else
                                        return "stopped"
                                    end if
                                end tell
                            else
                                return "not_running"
                            end if
                        end tell
                        '''
                        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
                        
                        if result.stdout.strip() not in ["stopped", "not_running", ""]:
                            info = result.stdout.strip().split("|")
                            if len(info) >= 2:
                                self.songTitle.setStringValue_(info[0])
                                self.artistName.setStringValue_(info[1][:15])
                                
                                if len(info) >= 5:
                                    if "paused" in info[4]:
                                        self.playBtn.setTitle_("▶")
                                    else:
                                        self.playBtn.setTitle_("❚❚")
                                
                                if len(info) >= 4:
                                    try:
                                        position = float(info[2])
                                        duration = float(info[3])
                                        if duration > 0:
                                            percentage = (position / duration) * 100
                                            # Only update if user hasn't touched slider in last 5 seconds
                                            if time.time() - self.lastProgressSliderTouch > 5.0:
                                                self.progressSlider.setDoubleValue_(percentage)
                                    except:
                                        pass
                        else:
                            self.songTitle.setStringValue_("Locked In")
                            self.artistName.setStringValue_("")
                            self.playBtn.setTitle_("▶")
                except Exception as e:
                    print(f"Media update error: {e}")
                    self.songTitle.setStringValue_("Locked In")
                    self.artistName.setStringValue_("")
                    self.playBtn.setTitle_("▶")
                
                # Schedule next update in 1 second for smoother updates
                threading.Timer(1.0, self.updateMediaInfo).start()
            
            threading.Thread(target=update).start()
        
        def playPause_(self, sender):
            # Update button immediately - no spam check, always respond instantly
            if self.playBtn.title() == "❚❚":
                self.playBtn.setTitle_("▶")
            else:
                self.playBtn.setTitle_("❚❚")

            # Send the command in background
            threading.Thread(target=lambda: subprocess.run(
                ['osascript', '-e', 'tell application "Spotify" to playpause'], capture_output=True, timeout=0.5
            )).start()
        
        def nextTrack_(self, sender):
            if not self.checkSpam_("nextTrack"):
                threading.Thread(target=lambda: subprocess.run(
                    ['osascript', '-e', 'tell application "Spotify" to next track'], capture_output=True
                )).start()
        
        def previousTrack_(self, sender):
            if not self.checkSpam_("previousTrack"):
                threading.Thread(target=lambda: subprocess.run(
                    ['osascript', '-e', 'tell application "Spotify" to previous track'], capture_output=True
                )).start()
        
        def seekTrack_(self, sender):
            """Seek to position in track based on slider - smooth 60fps with debounced commands"""
            self.lastProgressSliderTouch = time.time()  # Mark slider as being touched
            currentTime = time.time()

            # Store the current slider value for debounced execution
            self.pendingSeekValue = self.progressSlider.doubleValue()

            # Only execute command if 0.1 seconds have passed since last command (max 10 updates/sec)
            if currentTime - self.lastSeekCommandTime > 0.1:
                self.lastSeekCommandTime = currentTime
                seekValue = self.pendingSeekValue

                # Execute in background thread to not block UI
                def executeSeek():
                    try:
                        # Get current track duration from Spotify
                        script = '''
                        tell application "Spotify"
                            set trackDuration to (duration of current track) / 1000
                            return trackDuration
                        end tell
                        '''
                        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=0.5)
                        duration = float(result.stdout.strip())
                        position = (seekValue / 100) * duration

                        # Set position in Spotify
                        seekScript = f'''
                        tell application "Spotify"
                            set player position to {position}
                        end tell
                        '''
                        subprocess.run(['osascript', '-e', seekScript], capture_output=True, timeout=0.5)
                    except:
                        pass

                threading.Thread(target=executeSeek).start()
        
        def changeVolume_(self, sender):
            """Change system volume based on slider - smooth 60fps with debounced commands"""
            self.lastVolumeSliderTouch = time.time()  # Mark slider as being touched
            currentTime = time.time()

            # Store the current slider value for debounced execution
            self.pendingVolumeValue = self.volumeSlider.doubleValue()

            # Only execute command if 0.05 seconds have passed since last command (max 20 updates/sec for volume)
            if currentTime - self.lastVolumeCommandTime > 0.05:
                self.lastVolumeCommandTime = currentTime
                volume = int(self.pendingVolumeValue)

                # Execute in background thread to not block UI
                def executeVolumeChange():
                    try:
                        # Use osascript to set system volume (0-100 scale)
                        script = f'set volume output volume {volume}'
                        subprocess.run(['osascript', '-e', script], capture_output=True, timeout=0.3)
                    except:
                        pass

                threading.Thread(target=executeVolumeChange).start()
        
        def createAppIconButton_x_y_action_(self, appPath, x, y, action):
            """Create a button with actual app icon"""
            button = NSButton.alloc().initWithFrame_(NSMakeRect(x, y, 40, 40))

            # Load the app icon
            workspace = NSWorkspace.sharedWorkspace()
            icon = workspace.iconForFile_(appPath)
            if icon:
                icon.setSize_(NSSize(32, 32))
                button.setImage_(icon)

            button.setTitle_("")  # No text, only icon
            button.setBezelStyle_(0)  # No bezel for cleaner look
            button.setBordered_(False)
            button.setImagePosition_(2)  # Image only
            button.setTarget_(self)
            button.setAction_(objc.selector(action, signature=b'v@:@'))
            self.addSubview_(button)
            return button

        def createEmptyQuickAccessButtonAtX_y_index_(self, x, y, index):
            """Create a clean text button that says 'Configure in settings'"""
            # Container view to hold button and text labels
            container = NSView.alloc().initWithFrame_(NSMakeRect(x, y, 40, 40))

            # Invisible button for clicking
            button = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 40, 40))
            button.setTitle_("")
            button.setBezelStyle_(0)
            button.setBordered_(False)
            button.setTarget_(self)
            button.setAction_(objc.selector(self.openSettings_, signature=b'v@:@'))
            button.setWantsLayer_(True)
            button.layer().setBackgroundColor_(NSColor.clearColor().CGColor())
            container.addSubview_(button)

            # First line: "Configure in" - relative to container
            line1 = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 18, 40, 12))
            line1.setStringValue_("Configure in")
            line1.setBezeled_(False)
            line1.setDrawsBackground_(False)
            line1.setEditable_(False)
            line1.setSelectable_(False)
            line1.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.5, 0.5, 0.55, 0.9))
            line1.setFont_(NSFont.systemFontOfSize_(6))
            line1.setAlignment_(1)  # Center align
            container.addSubview_(line1)

            # Second line: "settings" - relative to container
            line2 = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 8, 40, 12))
            line2.setStringValue_("settings")
            line2.setBezeled_(False)
            line2.setDrawsBackground_(False)
            line2.setEditable_(False)
            line2.setSelectable_(False)
            line2.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(0.5, 0.5, 0.55, 0.9))
            line2.setFont_(NSFont.systemFontOfSize_(6))
            line2.setAlignment_(1)  # Center align
            container.addSubview_(line2)

            self.addSubview_(container)
            return container


        def openSettings_(self, sender):
            """Open settings window when gear button is clicked"""
            # Call showSettings_ directly on self since we're in ControlPanelView
            self.showSettings_(sender)


        def loadSettings(self):
            """Load settings from plist file"""
            try:
                import plistlib
                import os

                # Use ~/Library/Preferences for settings
                prefs_path = os.path.expanduser("~/Library/Preferences/com.dynamicisland.plist")

                if os.path.exists(prefs_path):
                    with open(prefs_path, 'rb') as f:
                        settings = plistlib.load(f)
                        self.quickAppPaths = settings.get('quickAppPaths', [None, None, None, None])
                        self.presetApps = settings.get('presetApps', {
                            "Programming": [],
                            "Chilling": [],
                            "Debugging": [],
                            "Focus Mode": []
                        })
                else:
                    self.quickAppPaths = [None, None, None, None]
                    self.presetApps = {
                        "Programming": [],
                        "Chilling": [],
                        "Debugging": [],
                        "Focus Mode": []
                    }
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.quickAppPaths = [None, None, None, None]
                self.presetApps = {
                    "Programming": [],
                    "Chilling": [],
                    "Debugging": [],
                    "Focus Mode": []
                }

        def saveSettings(self):
            """Save settings to plist file"""
            try:
                import plistlib
                import os

                # Prepare settings dictionary
                settings = {
                    'quickAppPaths': self.quickAppPaths
                }

                if hasattr(self, 'presetApps'):
                    settings['presetApps'] = self.presetApps

                # Save to ~/Library/Preferences
                prefs_path = os.path.expanduser("~/Library/Preferences/com.dynamicisland.plist")
                os.makedirs(os.path.dirname(prefs_path), exist_ok=True)

                with open(prefs_path, 'wb') as f:
                    plistlib.dump(settings, f)

                print("Settings saved successfully")
            except Exception as e:
                print(f"Error saving settings: {e}")
        
        def createCapsuleButton_x_y_action_(self, title, x, y, action):
            """Create a fully rounded capsule button"""
            button = NSButton.alloc().initWithFrame_(NSMakeRect(x, y, 146, 22))  # 50% thinner
            button.setTitle_(title)
            button.setBezelStyle_(1)  # Regular button with opacity
            button.setFont_(NSFont.boldSystemFontOfSize_(11))
            button.setTarget_(self)
            button.setAction_(objc.selector(action, signature=b'v@:@'))
            button.setAlphaValue_(1.0)  # Full opacity
            self.addSubview_(button)
            return button
        
        def createSetupButton_x_y_action_(self, title, x, y, action):
            """Create a rounded button"""
            button = NSButton.alloc().initWithFrame_(NSMakeRect(x, y, 119, 15))  # Reduced by 8px from right
            button.setTitle_(title)
            button.setBezelStyle_(1)  # Regular button with opacity
            button.setFont_(NSFont.systemFontOfSize_(9))
            button.setTarget_(self)
            button.setAction_(objc.selector(action, signature=b'v@:@'))
            button.setAlphaValue_(1.0)  # Full opacity
            self.addSubview_(button)
            return button

        def createSetupButton_x_y_action_gradient_(self, title, x, y, action, gradientColors):
            """Create a button with custom colored background"""
            # Use the average of the two gradient colors for a solid dark color
            avgR = (gradientColors[0][0] + gradientColors[1][0]) / 2
            avgG = (gradientColors[0][1] + gradientColors[1][1]) / 2
            avgB = (gradientColors[0][2] + gradientColors[1][2]) / 2

            button = NSButton.alloc().initWithFrame_(NSMakeRect(x, y, 119, 15))
            button.setTitle_(title)
            button.setBezelStyle_(0)  # No bezel
            button.setBordered_(False)
            button.setFont_(NSFont.systemFontOfSize_weight_(9, 0.3))
            button.setTarget_(self)
            button.setAction_(objc.selector(action, signature=b'v@:@'))
            button.setWantsLayer_(True)
            button.layer().setBackgroundColor_(NSColor.colorWithRed_green_blue_alpha_(avgR, avgG, avgB, 1.0).CGColor())
            button.layer().setCornerRadius_(4)
            button.layer().setBorderWidth_(0.5)
            button.layer().setBorderColor_(NSColor.colorWithRed_green_blue_alpha_(avgR + 0.1, avgG + 0.1, avgB + 0.1, 0.5).CGColor())
            self.addSubview_(button)

            return button
        
        def checkSpam_(self, buttonName):
            """Anti-spam protection - 1 second cooldown"""
            currentTime = time.time()
            if buttonName in self.lastClickTime:
                if currentTime - self.lastClickTime[buttonName] < 1.0:
                    return True  # Is spam
            self.lastClickTime[buttonName] = currentTime
            return False
        
        # Quick Access actions
        def launchQuickApp0_(self, sender):
            self.launchQuickApp_(0)
        
        def launchQuickApp1_(self, sender):
            self.launchQuickApp_(1)
        
        def launchQuickApp2_(self, sender):
            self.launchQuickApp_(2)
        
        def launchQuickApp3_(self, sender):
            self.launchQuickApp_(3)
        
        def launchQuickApp_(self, index):
            if index < len(self.quickAppPaths):
                appPath = self.quickAppPaths[index]
                if not self.checkSpam_(f"quickapp_{index}"):
                    threading.Thread(target=lambda: subprocess.run(
                        ['open', appPath], capture_output=True
                    )).start()
        
        def updateQuickAccessButton_withPath_(self, index, appPath):
            """Update a Quick Access button with new app"""
            if index < len(self.quickButtons) and index < len(self.quickAppPaths):
                self.quickAppPaths[index] = appPath

                # Get position of old button
                oldButton = self.quickButtons[index]
                frame = oldButton.frame()

                # Remove old button
                oldButton.removeFromSuperview()

                # Create new button with updated app
                actions = [self.launchQuickApp0_, self.launchQuickApp1_, self.launchQuickApp2_, self.launchQuickApp3_]
                if appPath:
                    newButton = self.createAppIconButton_x_y_action_(appPath, frame.origin.x, frame.origin.y, actions[index])
                else:
                    newButton = self.createEmptyQuickAccessButtonAtX_y_index_(frame.origin.x, frame.origin.y, index)
                self.quickButtons[index] = newButton

                # Save settings after updating
                self.saveSettings()
        
        # Setup actions
        def setupProgramming_(self, sender):
            if not self.checkSpam_("programming"):
                self.launchPresetApps_("Programming")

        def setupChilling_(self, sender):
            if not self.checkSpam_("chilling"):
                self.launchPresetApps_("Chilling")

        def setupDebugging_(self, sender):
            if not self.checkSpam_("debugging"):
                self.launchPresetApps_("Debugging")

        def setupFocus_(self, sender):
            if not self.checkSpam_("focus"):
                self.launchPresetApps_("Focus Mode")

        def launchPresetApps_(self, presetName):
            """Launch all apps configured for a preset"""
            def launch():
                apps = self.presetApps.get(presetName, [])
                if apps:
                    print(f"Launching {len(apps)} apps for preset: {presetName}")
                    for appPath in apps:
                        try:
                            subprocess.run(['open', appPath], capture_output=True)
                            print(f"Launched: {os.path.basename(appPath)}")
                        except Exception as e:
                            print(f"Failed to launch {appPath}: {e}")
                else:
                    print(f"No apps configured for preset: {presetName}")
            threading.Thread(target=launch).start()
    
    class DynamicIslandView(NSView):
        def initWithFrame_(self, frame):
            self = objc.super(DynamicIslandView, self).initWithFrame_(frame)
            if self:
                self.isHovering = False
                self.isExpanded = False
                self.controlPanel = None
                self.mouseCheckTimer = None
                
                # Create tracking area
                trackingArea = NSTrackingArea.alloc().initWithRect_options_owner_userInfo_(
                    self.bounds(),
                    NSTrackingMouseEnteredAndExited | NSTrackingActiveAlways | NSTrackingInVisibleRect,
                    self,
                    None
                )
                self.addTrackingArea_(trackingArea)
            return self
        
        def setupControlPanel(self):
            if not self.controlPanel:
                self.controlPanel = ControlPanelView.alloc().initWithFrame_(self.bounds())
                self.controlPanel.setHidden_(True)
                self.addSubview_(self.controlPanel)
        
        def showControlPanel(self):
            if self.controlPanel:
                self.controlPanel.setFrame_(self.bounds())
                self.controlPanel.setHidden_(False)
        
        def animateWindow_toFrame_duration_(self, window, targetFrame, duration):
            NSAnimationContext.beginGrouping()
            NSAnimationContext.currentContext().setDuration_(duration)
            window.animator().setFrame_display_(targetFrame, True)
            NSAnimationContext.endGrouping()
        
        def acceptsFirstResponder(self):
            return True
        
        def drawRect_(self, rect):
            # Draw black rounded rectangle
            NSColor.blackColor().set()
            cornerRadius = 22.5 if rect.size.width <= 210 else 30
            path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
                self.bounds(), cornerRadius, cornerRadius
            )
            path.fill()
        
        def mouseEntered_(self, event):
            if self.isExpanded:
                return

            # Auto-expand on hover
            self.isHovering = True
            self.isExpanded = True
            self.setupControlPanel()

            window = self.window()

            # Calculate centered expansion frame
            screen = NSScreen.mainScreen()
            screenFrame = screen.frame()
            expandedWidth = 700
            expandedHeight = 130
            expandedX = (screenFrame.size.width - expandedWidth) / 2
            expandedY = screenFrame.size.height - expandedHeight + 12

            frame = NSMakeRect(expandedX, expandedY, expandedWidth, expandedHeight)

            self.setNeedsDisplay_(True)
            self.animateWindow_toFrame_duration_(window, frame, 0.25)
            
            # Show controls after animation
            def showControls():
                time.sleep(0.2)
                self.performSelectorOnMainThread_withObject_waitUntilDone_(
                    objc.selector(self.showControlPanel, signature=b'v@:'),
                    None,
                    False
                )
            threading.Thread(target=showControls).start()
            
            # Strong haptic feedback pulse on hover
            performer = NSHapticFeedbackManager.defaultPerformer()
            if performer:
                # Pattern 1 = alignment feedback (stronger)
                performer.performFeedbackPattern_performanceTime_(1, 0)
        
        def mouseExited_(self, event):
            if not self.isHovering:
                return
            
            # Start a timer to check mouse position
            self.checkMousePositionDelayed()
        
        def checkMousePositionDelayed(self):
            """Check mouse position after a small delay to ensure proper closing"""
            def checkPosition():
                time.sleep(0.1)  # Small delay to let mouse settle
                self.performSelectorOnMainThread_withObject_waitUntilDone_(
                    objc.selector(self.checkAndClose, signature=b'v@:'),
                    None,
                    False
                )
            threading.Thread(target=checkPosition).start()
        
        def checkAndClose(self):
            """Actually check mouse position and close if outside buffer"""
            if not self.isHovering or not self.isExpanded:
                return
            
            window = self.window()
            mouseLocation = NSEvent.mouseLocation()
            windowFrame = window.frame()
            
            # Add 10px buffer zone around the window
            expandedFrame = NSMakeRect(
                windowFrame.origin.x - 10,
                windowFrame.origin.y - 10,
                windowFrame.size.width + 20,
                windowFrame.size.height + 20
            )
            
            if not NSPointInRect(mouseLocation, expandedFrame):
                self.isHovering = False
                self.isExpanded = False
                
                if self.controlPanel:
                    self.controlPanel.setHidden_(True)

                # Calculate centered contracted frame
                screen = NSScreen.mainScreen()
                screenFrame = screen.frame()
                contractedWidth = 200
                contractedHeight = 45
                contractedX = (screenFrame.size.width - contractedWidth) / 2
                contractedY = screenFrame.size.height - contractedHeight + 12

                frame = NSMakeRect(contractedX, contractedY, contractedWidth, contractedHeight)

                self.setNeedsDisplay_(True)
                self.animateWindow_toFrame_duration_(window, frame, 0.2)
            else:
                # Mouse is still in buffer zone, check again
                self.performSelector_withObject_afterDelay_(
                    objc.selector(self.checkAndClose, signature=b'v@:'),
                    None,
                    0.5
                )
        
        def mouseDown_(self, event):
            # Click functionality removed - expansion now handled by hover
            # Haptic feedback on click
            performer = NSHapticFeedbackManager.defaultPerformer()
            if performer:
                performer.performFeedbackPattern_performanceTime_(0, 0)
    
    class DynamicIslandDelegate(NSObject):
        def applicationDidFinishLaunching_(self, notification):
            screen = NSScreen.mainScreen()
            screenFrame = screen.frame()
            
            # Position at top of screen
            width = 200
            height = 45
            x = (screenFrame.size.width - width) / 2
            y = screenFrame.size.height - height + 12
            
            # Create window
            self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                NSMakeRect(x, y, width, height),
                NSWindowStyleMaskBorderless,
                2,
                False
            )
            
            # Window properties
            self.window.setLevel_(25)  # Status window level
            self.window.setOpaque_(False)
            self.window.setBackgroundColor_(NSColor.clearColor())
            self.window.setHasShadow_(True)
            self.window.setIgnoresMouseEvents_(False)
            self.window.setAcceptsMouseMovedEvents_(True)
            # Fixed: Ensure window appears on all spaces and can't be moved
            self.window.setCollectionBehavior_(1 << 0 | 1 << 7 | 1 << 4)  # Added NSWindowCollectionBehaviorStationary
            self.window.setMovable_(False)  # Prevent manual window movement
            
            # Create content view
            contentView = DynamicIslandView.alloc().initWithFrame_(
                NSMakeRect(0, 0, width, height)
            )
            self.window.setContentView_(contentView)
            
            # Show window
            self.window.makeKeyAndOrderFront_(None)
            self.window.orderFrontRegardless()
            self.window.makeFirstResponder_(contentView)

            # Store original position for repositioning
            self.originalPosition = NSMakeRect(x, y, width, height)

            # Add notification observer to recenter when screen configuration changes
            NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
                self,
                objc.selector(self.screenDidChange_, signature=b'v@:@'),
                "NSApplicationDidChangeScreenParametersNotification",
                None
            )

            # Start position monitoring timer to fix drift
            self.startPositionMonitoring()

            print("Dynamic Island Clean running - optimized for performance")

        def screenDidChange_(self, notification):
            """Recenter window when screen configuration changes"""
            self.recenterWindow()

        def recenterWindow(self):
            """Force window back to center of screen"""
            screen = NSScreen.mainScreen()
            screenFrame = screen.frame()

            # Recalculate center position
            width = 200 if not self.window.contentView().isExpanded else 700
            height = 45 if not self.window.contentView().isExpanded else 130
            x = (screenFrame.size.width - width) / 2
            y = screenFrame.size.height - height + 12

            # Update window position
            newFrame = NSMakeRect(x, y, width, height)
            self.window.setFrame_display_(newFrame, True)

        def startPositionMonitoring(self):
            """Monitor window position and fix drift"""
            def monitor():
                while True:
                    try:
                        time.sleep(5)  # Check every 5 seconds

                        # Check if window has drifted from center
                        screen = NSScreen.mainScreen()
                        screenFrame = screen.frame()
                        windowFrame = self.window.frame()

                        # Calculate expected center position
                        expectedX = (screenFrame.size.width - windowFrame.size.width) / 2
                        expectedY = screenFrame.size.height - windowFrame.size.height + 12

                        # Allow 5px tolerance for positioning
                        if (abs(windowFrame.origin.x - expectedX) > 5 or
                            abs(windowFrame.origin.y - expectedY) > 5):
                            # Window has drifted, recenter it
                            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                                objc.selector(self.recenterWindow, signature=b'v@:'),
                                None,
                                False
                            )
                    except:
                        pass

            threading.Thread(target=monitor, daemon=True).start()
    
    # Run the app
    app = NSApplication.sharedApplication()
    delegate = DynamicIslandDelegate.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()
    
except ImportError:
    print("PyObjC not installed. Installing...")
    import subprocess
    subprocess.run(['pip3', 'install', 'pyobjc-framework-Cocoa'])
    print("Please run the script again.")