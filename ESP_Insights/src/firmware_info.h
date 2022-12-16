#pragma once
#include <Arduino.h>

#include <esp_app_format.h>
// #include <esp_app_desc.h>
#include <esp_ota_ops.h>
// #include <esp_system.h>

#include "esp_log.h"


#include <esp32-hal-cpu.h>
#include <esp_flash.h>


#define HASH_LEN 32 /* SHA-256 digest length */

static void print_sha256 (const uint8_t *image_hash, const char *label)
{
    char hash_print[HASH_LEN * 2 + 1];
    hash_print[HASH_LEN * 2] = 0;
    for (int i = 0; i < HASH_LEN; ++i) {
        sprintf(&hash_print[i * 2], "%02x", image_hash[i]);
    }
    ESP_LOGI("shaELF", "%s: %s", label, hash_print);
}

void show_firmware_description(void){

    // esp_app_desc_t info = esp_app_get_description();
    esp_app_desc_t fw_info;
    if (esp_ota_get_partition_description(esp_ota_get_running_partition(), &fw_info) == ESP_OK) {
        Serial.printf("--+ Firmware info: +--\n");
        Serial.printf("project_name: %s\n", fw_info.project_name);
        Serial.printf("version: %s\n", fw_info.version);
        Serial.printf("time: %s\n", fw_info.time);
        Serial.printf("date: %s\n", fw_info.date);
        Serial.printf("idf_ver: %s\n", fw_info.idf_ver);
        char hash_print[HASH_LEN * 2 + 1];
        hash_print[HASH_LEN * 2] = 0;
        for (int i = 0; i < HASH_LEN; ++i) sprintf(&hash_print[i * 2], "%02x", fw_info.app_elf_sha256[i]);
        Serial.printf("app_elf_sha256: %s\n", hash_print);

        // Get sha256 digest for running partition
        uint8_t sha_256[HASH_LEN] = { 0 };
        esp_partition_get_sha256(esp_ota_get_running_partition(), sha_256);
        print_sha256(sha_256, "SHA-256 for current app running partition: ");

        Serial.printf("\n--+  -----------   +--\n");
    }

    // Another way:
    // esp_app_desc_t app_info2;
    // if (esp_ota_get_partition_description(esp_partition_get(esp_partition_find(ESP_PARTITION_TYPE_APP,ESP_PARTITION_SUBTYPE_APP_OTA_0, "ota_0")), &app_info2) == ESP_OK){
    //     Serial.printf("--+ Firmware info app 1: +--\n");
    //     Serial.printf("project_name: %s\n", info->project_name);
    //     Serial.printf("version: %s\n", info->version);
    //     Serial.printf("time: %s\n", info->time);
    //     Serial.printf("date: %s\n", info->date);
    //     Serial.printf("idf_ver: %s\n", info->idf_ver);
    //     Serial.printf("app_elf_sha256: ");
    //     // for (int i=0;i < (sizeof (info->app_elf_sha256) /sizeof (info->app_elf_sha256[0]));i++) printf("%c",info->app_elf_sha256[i]);
    //     for (int i=0;i < 32;i++) printf("%u", info->app_elf_sha256[i]);
    //     Serial.printf("\n--+  -----------   +--\n");
    // }

    delay(2000);

}


void show_flash_info(void){


    esp_err_t status;
    char err_msg[20];
    
    esp_flash_t *chip;
    uint32_t out_id;
    // if ((status = esp_flash_read_id(&chip, &out_id)) != ESP_OK) log_e("esp_flash_read_id error: %s", esp_err_to_name_r(status, err_msg, sizeof(err_msg)));
    if ((status = esp_flash_read_id(NULL, &out_id)) != ESP_OK) log_e("esp_flash_read_id error: %s", esp_err_to_name_r(status, err_msg, sizeof(err_msg)));
    else{
        log_i("Chip out_id: %d", out_id);
        // log_i("Chip read mode: %d size: %d id: %d", chip->read_mode, chip->size, chip->chip_id);
    }
    
    esp_flash_t *unique_chip;
    uint64_t unique_out_id;
    // if ((status = esp_flash_read_unique_chip_id(&unique_chip, &unique_out_id)) != ESP_OK) log_e("esp_flash_read_id error: %s", esp_err_to_name_r(status, err_msg, sizeof(err_msg)));
    if ((status = esp_flash_read_unique_chip_id(NULL, &unique_out_id)) != ESP_OK) log_e("esp_flash_read_id error: %s", esp_err_to_name_r(status, err_msg, sizeof(err_msg)));
    else{
        log_i("Chip unique out_id: %" PRId64 "", unique_out_id);
        // log_i("Chip unique read mode: %d size: %d id: %d", chip->read_mode, chip->size, chip->chip_id);
    }

    log_i("Flash mode: %02x ", ESP.getFlashChipMode());
    log_i("CPU flash freq: %d MHz, xTal: %d MHz, APB: %d Hz", getCpuFrequencyMhz(), getXtalFrequencyMhz(), getXtalFrequencyMhz());

}
