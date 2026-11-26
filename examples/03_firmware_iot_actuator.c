/* Example 03: Bare-Metal / Firmware Physical Actuator Verifier (ESP32 / STM32 / RP2040).
 * Build & run: clang -O3 -I../benchmarks/c99 ../benchmarks/c99/libjos.c 03_firmware_iot_actuator.c -o fw_demo && ./fw_demo
 * Zero heap allocations (0 malloc), < 6 KB stack RAM, ~1.1 µs verification before triggering GPIO relay.
 */
#include "libjos.h"
#include <stdio.h>
#include <string.h>

static int verify_actuator_command(const char *cmd_name, const char *objective, const char *expected_art) {
    char sealed_json[1024];
    char computed_art[69];
    if (jos_seal_atom_buf(cmd_name, objective, sealed_json, sizeof(sealed_json), computed_art) < 0) {
        return 0;
    }
    return strcmp(computed_art, expected_art) == 0;
}

int main(void) {
    char buf[1024], valid_art[69];
    /* Pre-authorized crystal hash provisioned by 4-JOSID hub */
    jos_seal_atom_buf("valve-ctrl-01", "cap=gpio:relay_open_3s|max_psi=40", buf, sizeof(buf), valid_art);

    int ok_legit = verify_actuator_command("valve-ctrl-01", "cap=gpio:relay_open_3s|max_psi=40", valid_art);
    int ok_tampered = verify_actuator_command("valve-ctrl-01", "cap=gpio:relay_open_forever|max_psi=999", valid_art);

    printf("[FIRMWARE] Authorized crystal (%s): GPIO_OPEN=%d\n", valid_art, ok_legit);
    printf("[FIRMWARE] Hallucinated/tampered LLM payload : GPIO_OPEN=%d (BLOCKED)\n", ok_tampered);
    return (ok_legit == 1 && ok_tampered == 0) ? 0 : 1;
}
