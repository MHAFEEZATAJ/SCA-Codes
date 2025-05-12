#include <Arduino.h>
#include "aes.h"

#define TRIGGER_PIN 7  // Define the trigger pin

uint8_t key[16] = {0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 
                   0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c};

uint8_t plaintext[16];  // Input buffer

void setup() {
    Serial.begin(115200);
    while (!Serial);  // Wait for serial connection

    pinMode(TRIGGER_PIN, OUTPUT);
    digitalWrite(TRIGGER_PIN, LOW);

    Serial.println("AES Ready! Send 32 hex chars (16 bytes).");

    // Set AES key
    AES128_ECB_indp_setkey(key);

    // Debug: Print Key
    Serial.print("Key: ");
    for (int i = 0; i < 16; i++) {
        if (key[i] < 16) Serial.print("0");
        Serial.print(key[i], HEX);
        Serial.print(" ");
    }
    Serial.println();
}

void loop() {
    char hexBuffer[33];  // Buffer to store the 32-character hex input + null terminator
    int bytesRead = 0;

    // Wait until we receive exactly 32 characters
    while (bytesRead < 32) {
        if (Serial.available()) {
            char c = Serial.read();
            if (isxdigit(c)) {  // Ensure only valid hex chars are read
                hexBuffer[bytesRead++] = c;
            }
        }
    }
    hexBuffer[32] = '\0';  // Null-terminate the string

    // Convert hex string to byte array
    for (int i = 0; i < 16; i++) {
        char hexByte[3] = {hexBuffer[i * 2], hexBuffer[i * 2 + 1], '\0'};
        plaintext[i] = strtol(hexByte, NULL, 16);
    }

    // Debug: Print received plaintext
    Serial.print("Plaintext: ");
    for (int i = 0; i < 16; i++) {
        if (plaintext[i] < 16) Serial.print("0");
        Serial.print(plaintext[i], HEX);
        Serial.print(" ");
    }
    Serial.println();

    Serial.println("Key Ready! Plaintext Ready! Starting Encryption...");

    digitalWrite(TRIGGER_PIN, HIGH);  // Set trigger HIGH before encryption

    // Encrypt the plaintext (modifies plaintext in place)
    AES128_ECB_indp_crypto(plaintext);

    digitalWrite(TRIGGER_PIN, LOW);  // Set trigger LOW after encryption

    // Debug: Print Ciphertext (modified plaintext)
    Serial.print("Ciphertext: ");
    for (int i = 0; i < 16; i++) {
        if (plaintext[i] < 16) Serial.print("0");
        Serial.print(plaintext[i], HEX);
        Serial.print(" ");
    }
    Serial.println();
    
    Serial.flush();  // Ensure all data is fully sent
}
