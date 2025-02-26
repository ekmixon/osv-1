/*
 * Copyright (C) 2014 Huawei Technologies Duesseldorf GmbH
 *
 * This work is open source software, licensed under the terms of the
 * BSD license as described in the LICENSE file in the top-level directory.
 */

cmdline_addr = . + 0x200 // 512 bytes after start of image
target = . + 0x10000

.text
.align 16

_head:
	/* Image header expected by Linux boot-loaders, see
	 * Documentation/arm64/booting.txt in Linux tree for format description
	*/
	b prestart		// jump to actual prestart
	.long 0			// reserved
	.long 0x00080000	// image load offset
	.long 0x00000000
	.long 0			// image size will be populated by Makefile
	.long 0
	.long 0			// unused informative flags, Xen/QEMU
	.long 0			//    image loaders ignore this field
	.long 0			// reserved
	.long 0			// reserved
	.long 0			// reserved
	.long 0			// reserved
	.long 0			// reserved
	.long 0			// reserved
	.byte 0x41		// magic number, "ARM\x64"
	.byte 0x52
	.byte 0x4d
	.byte 0x64
	.long 0			// reserved

.globl prestart
.hidden prestart
prestart: // x4 = 0x40080000 set by qemu bootloader
        mov     x5, x0     /* save device tree blob addr */
        adr     x4, cmdline_addr
        adr     x3, target /* elf header start */

        // load entry point from ELF header + 24
        ldr     w0, [x3, #24]
        ldr     w1, [x3, #28]

        orr     x0, x0, x1, LSL #32
        br      x0
