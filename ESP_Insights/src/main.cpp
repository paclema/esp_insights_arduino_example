#include <Arduino.h>

#include <WiFi.h>

const char* ssid     = "wifiname";
const char* password = "wifipass";

#define ESP_INSIGHTS_AUTH_KEY "qwP4t1W1W6Sb6SeqwP4taKaZ1W6SbGciOiR58wZrunHaKaZEsAvqwP4t1W6SizNQ"
#define METRICS_DUMP_INTERVAL           10 * 1000
#define METRICS_DUMP_INTERVAL_TICKS     (METRICS_DUMP_INTERVAL / portTICK_RATE_MS)
static const char *TAG_INSIGHTS = "INSIGHTS";

unsigned long lastPublishedMetrics = millis();
bool insightsEnabled = true;
bool insightsLoop = true;

#include "esp32-hal-log.h"
#define LOG_LOCAL_LEVEL ESP_LOG_VERBOSE
#include "esp_log.h"
#include <esp_insights.h>
#include "esp_diagnostics_system_metrics.h"
#include <esp_diagnostics_metrics.h>
#include <esp_diagnostics_variables.h>
#include "esp_rmaker_utils.h"

#include <firmware_info.h>

void TaskEspInsights( void *pvParameters ){
    while (true) {
        esp_diag_heap_metrics_dump();
        esp_diag_wifi_metrics_dump();
        log_d("ESP-Insights heap and wifi metrics updated from xTask");
        vTaskDelay(METRICS_DUMP_INTERVAL_TICKS*2);
    }
}

void init_insights(void){
    esp_rmaker_time_sync_init(NULL);
    esp_insights_config_t config = {
      .log_type = ESP_DIAG_LOG_TYPE_ERROR | ESP_DIAG_LOG_TYPE_WARNING | ESP_DIAG_LOG_TYPE_EVENT,
      .auth_key = ESP_INSIGHTS_AUTH_KEY,
    };

    esp_err_t ret = esp_insights_init(&config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG_INSIGHTS, "Failed to initialize ESP Insights, err:0x%x", ret);
    }
    // ESP_ERROR_CHECK(ret);

    esp_diag_heap_metrics_dump();
    esp_diag_wifi_metrics_dump();

    // Register a Metric:
    esp_diag_metrics_register("ControlDeviceStatus", "CDstatus", "ControlDevice current status", "AccessCtrl", ESP_DIAG_DATA_TYPE_UINT);
    // uint32_t statusNum = 12;
    // esp_diag_metrics_add_uint("CDstatus", statusNum);

    esp_diag_metrics_register("ControlDevice button count", "pushCount", "ControlDevice button push count", "AccessCtrl", ESP_DIAG_DATA_TYPE_UINT);
    

    // Register a Variable:
    esp_diag_variable_register("Wi-Fi", "lastEvent", "Last event", "Wi-Fi.Events", ESP_DIAG_DATA_TYPE_UINT);
    esp_diag_variable_add_uint("lastEvent", 7);
    
    esp_diag_variable_register("AccessCtrl", "lockStatus", "Lock status", "AccessCtrl.ControlDevice", ESP_DIAG_DATA_TYPE_STR);


    xTaskCreatePinnedToCore(
        TaskEspInsights
        ,  "EspInsights"
        ,  1024*4  // Stack size
        ,  NULL
        ,  1  // Priority
        ,  NULL 
        ,  ARDUINO_RUNNING_CORE);

}



static const char *insightsTAG = "esp_insights";

unsigned long currentLoopMillis = 0;
unsigned long previousMainLoopMillis = 0;

void setup() {

    // Open USB serial port
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    // esp_log_level_set("*", ESP_LOG_VERBOSE);
    esp_log_level_set("*", ESP_LOG_ERROR);
    esp_log_level_set("cpu_start", ESP_LOG_INFO);
    esp_log_level_set(insightsTAG, ESP_LOG_VERBOSE);
    // esp_log_level_set("esp_core_dump_elf", ESP_LOG_VERBOSE);

    show_flash_info();
    show_firmware_description();

    Serial.printf("\n\nConnecting to %s", ssid);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    init_insights();

    ESP_LOGI(TAG_INSIGHTS, "###  Looping time");
    log_i("###  Looping time");
}

int count = 0;  // Variable for debugging purpose
void loop() {

    currentLoopMillis = millis();

    if(insightsEnabled && insightsLoop && (currentLoopMillis-lastPublishedMetrics > METRICS_DUMP_INTERVAL)){
        lastPublishedMetrics = currentLoopMillis;
        count++;
        esp_diag_heap_metrics_dump();
        esp_diag_wifi_metrics_dump();
        log_d("ESP-Insights heap and wifi metrics updated from loop");
    }

    previousMainLoopMillis = currentLoopMillis;
}