#ifndef OPENMVPLUGIN_H
#define OPENMVPLUGIN_H

#include <QtConcurrent>
#include <QtCore>
#include <QtGui>
#include <QtGui/private/qzipreader_p.h>
#include <QtNetwork>
#include <QtSerialPort>
#include <QtWidgets>

#include <coreplugin/actionmanager/actioncontainer.h>
#include <coreplugin/actionmanager/actionmanager.h>
#include <coreplugin/editormanager/editormanager.h>
#include <coreplugin/fancyactionbar.h>
#include <coreplugin/fancytabwidget.h>
#include <coreplugin/icore.h>
#include <coreplugin/messagemanager.h>
#include <texteditor/texteditor.h>
#include <extensionsystem/iplugin.h>
#include <extensionsystem/pluginmanager.h>
#include <extensionsystem/pluginspec.h>
#include <utils/environment.h>
#include <utils/pathchooser.h>
#include <utils/styledbar.h>
#include <utils/synchronousprocess.h>

#include "openmvpluginserialport.h"
#include "openmvpluginio.h"
#include "openmvpluginfb.h"
#include "openmvterminal.h"
#include "histogram/openmvpluginhistogram.h"
#include "tools/thresholdeditor.h"
#include "tools/keypointseditor.h"
#include "tools/tag16h5.h"
#include "tools/tag25h7.h"
#include "tools/tag25h9.h"
#include "tools/tag36h10.h"
#include "tools/tag36h11.h"
#include "tools/tag36artoolkit.h"

#define ICON_PATH ":/openmv/openmv-media/icons/openmv-icon/openmv.png"
#define SPLASH_PATH ":/openmv/openmv-media/splash/openmv-splash-slate/splash-small.png"
#define CONNECT_PATH ":/openmv/images/connect.png"
#define DISCONNECT_PATH ":/openmv/images/disconnect.png"
#define START_PATH ":/openmv/projectexplorer/images/run.png"
#define STOP_PATH ":/openmv/images/application-exit.png"

#define SETTINGS_GROUP "OpenMV"
#define EDITOR_MANAGER_STATE "EditorManagerState"
#define HSPLITTER_STATE "HSplitterState"
#define VSPLITTER_STATE "VSplitterState"
#define ZOOM_STATE "ZoomState"
#define JPG_COMPRESS_STATE "JPGCompressState"
#define DISABLE_FRAME_BUFFER_STATE "DisableFrameBufferState"
#define HISTOGRAM_COLOR_SPACE_STATE "HistogramColorSpace"
#define LAST_FIRMWARE_PATH "LastFirmwarePath"
#define LAST_FLASH_FS_ERASE_STATE "LastFlashFSEraseState"
#define LAST_BOARD_TYPE_STATE "LastBoardTypeState"
#define LAST_SERIAL_PORT_STATE "LastSerialPortState"
#define LAST_SAVE_IMAGE_PATH "LastSaveImagePath"
#define LAST_SAVE_TEMPLATE_PATH "LastSaveTemplatePath"
#define LAST_SAVE_DESCRIPTOR_PATH "LastSaveDescriptorPath"
#define LAST_OPEN_TERMINAL_SELECT "LastOpenTerminalSelect"
#define LAST_OPEN_TERMINAL_SERIAL_PORT "LastOpenTerminalSerialPort"
#define LAST_OPEN_TERMINAL_SERIAL_PORT_BAUD_RATE "LastOpenTerminalSerialPortBaudRate"
#define LAST_OPEN_TERMINAL_UDP_PORT "LastOpenTerminalUDPPort"
#define LAST_OPEN_TERMINAL_TCP_PORT "LastOpenTerminalTCPPort"
#define LAST_THRESHOLD_EDITOR_PATH "LastThresholdEditorPath"
#define LAST_EDIT_KEYPOINTS_PATH "LastEditKeypointsPath"
#define LAST_MERGE_KEYPOINTS_OPEN_PATH "LastMergeKeypointsOpenPath"
#define LAST_MERGE_KEYPOINTS_SAVE_PATH "LastMergeKeypointsSavePath"
#define LAST_APRILTAG_RANGE_MIN "LastAprilTagRangeMin"
#define LAST_APRILTAG_RANGE_MAX "LastAprilTagRangeMax"
#define LAST_APRILTAG_INCLUDE "LastAprilTagInclude"
#define LAST_APRILTAG_PATH "LastAprilTagPath"
#define RESOURCES_MAJOR "ResourcesMajor"
#define RESOURCES_MINOR "ResourcesMinor"
#define RESOURCES_PATCH "ResourcesPatch"

#define SERIAL_PORT_SETTINGS_GROUP "OpenMVSerialPort"
#define OPEN_TERMINAL_SETTINGS_GROUP "OpenMVOpenTerminal"
#define OPEN_TERMINAL_DISPLAY_NAME "DisplayName"
#define OPEN_TERMINAL_OPTION_INDEX "OptionIndex"
#define OPEN_TERMINAL_COMMAND_STR "CommandStr"
#define OPEN_TERMINAL_COMMAND_VAL "CommandVal"

#define OLD_API_MAJOR 1
#define OLD_API_MINOR 7
#define OLD_API_PATCH 0
#define OLD_API_BOARD "OMV2"

#define FRAME_SIZE_DUMP_SPACING     10 // in ms
#define GET_SCRIPT_RUNNING_SPACING  100 // in ms
#define GET_TX_BUFFER_SPACING       10 // in ms

#define FPS_AVERAGE_BUFFER_DEPTH    10 // in samples
#define ERROR_FILTER_MAX_SIZE       1000 // in chars
#define FPS_TIMER_EXPIRATION_TIME   2000 // in milliseconds

namespace OpenMV {
namespace Internal {

class OpenMVPlugin : public ExtensionSystem::IPlugin
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "org.qt-project.Qt.QtCreatorPlugin" FILE "OpenMV.json")

public:

    explicit OpenMVPlugin();
    bool initialize(const QStringList &arguments, QString *errorMessage);
    void extensionsInitialized();
    ExtensionSystem::IPlugin::ShutdownFlag aboutToShutdown();

public slots: // private

    void packageUpdate();
    void bootloaderClicked();
    void connectClicked(bool forceBootloader = false, QString forceFirmwarePath = QString(), int forceFlashFSErase = int());
    void disconnectClicked(bool reset = false);
    void startClicked();
    void stopClicked();
    void processEvents();
    void errorFilter(const QByteArray &data);
    void saveScript();
    void saveImage(const QPixmap &data);
    void saveTemplate(const QRect &rect);
    void saveDescriptor(const QRect &rect);
    void updateCam();
    void setPortPath(bool silent = false);
    void openTerminalAboutToShow();
    void openThresholdEditor();
    void openKeypointsEditor();
    void openAprilTagGenerator(apriltag_family_t *family);
    void openQRCodeGenerator();

signals:

    void workingDone();
    void disconnectDone();

private:

    QMap<QString, QAction *> aboutToShowExamplesRecursive(const QString &path, QMenu *parent);

    Core::Command *m_bootloaderCommand;
    Core::Command *m_saveCommand;
    Core::Command *m_resetCommand;
    Core::Command *m_docsCommand;
    Core::Command *m_forumsCommand;
    Core::Command *m_pinoutCommand;
    Core::Command *m_aboutCommand;
    Core::Command *m_connectCommand;
    Core::Command *m_disconnectCommand;
    Core::Command *m_startCommand;
    Core::Command *m_stopCommand;
    Core::ActionContainer *m_openTerminalMenu;
    Core::ActionContainer *m_machineVisionToolsMenu;
    Core::Command *m_thresholdEditorCommand;
    Core::Command *m_keypointsEditorCommand;
    Core::ActionContainer *m_AprilTagGeneratorSubmenu;
    Core::Command *m_tag16h5Command;
    Core::Command *m_tag25h7Command;
    Core::Command *m_tag25h9Command;
    Core::Command *m_tag36h10Command;
    Core::Command *m_tag36h11Command;
    Core::Command *m_tag36artoolkitCommand;
    Core::Command *m_QRCodeGeneratorCommand;

    Core::MiniSplitter *m_hsplitter;
    Core::MiniSplitter *m_vsplitter;

    QToolButton *m_zoom;
    QToolButton *m_jpgCompress;
    QToolButton *m_disableFrameBuffer;
    OpenMVPluginFB *m_frameBuffer;

    QComboBox *m_histogramColorSpace;
    OpenMVPluginHistogram *m_histogram;

    QToolButton *m_versionButton;
    QLabel *m_portLabel;
    QToolButton *m_pathButton;
    QLabel *m_fpsLabel;

    OpenMVPluginSerialPort *m_ioport;
    OpenMVPluginIO *m_iodevice;

    QElapsedTimer m_frameSizeDumpTimer;
    QElapsedTimer m_getScriptRunningTimer;
    QElapsedTimer m_getTxBufferTimer;

    QElapsedTimer m_timer;
    QQueue<qint64> m_queue;

    bool m_working;
    bool m_connected;
    bool m_running;
    int m_major;
    int m_minor;
    int m_patch;
    QString m_portName;
    QString m_portPath;

    QRegularExpression m_errorFilterRegex;
    QString m_errorFilterString;

    typedef struct openTerminalMenuData
    {
        QString displayName;
        int optionIndex;
        QString commandStr;
        int commandVal;
    }
    openTerminalMenuData_t;

    QList<openTerminalMenuData_t> m_openTerminalMenuData;

    bool openTerminalMenuDataContains(const QString &displayName)
    {
        foreach(const openTerminalMenuData_t &data, m_openTerminalMenuData)
        {
            if(data.displayName == displayName)
            {
                return true;
            }
        }

        return false;
    }
};

} // namespace Internal
} // namespace OpenMV

#endif // OPENMVPLUGIN_H
