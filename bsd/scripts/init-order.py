import fnmatch
import os
import os.path
import re
import sys

includes = ['*.c', '*.h'] # for files only
# transform glob patterns to regular expressions
includes = r'|'.join([fnmatch.translate(x) for x in includes])

# lowest comes first
order_one = {
    'SI_SUB_DUMMY': 0,
    'SI_SUB_DONE': 1,
    'SI_SUB_TUNABLES': 7340032,
    'SI_SUB_COPYRIGHT': 8388609,
    'SI_SUB_SETTINGS': 8912896,
    'SI_SUB_MTX_POOL_STATIC': 9437184,
    'SI_SUB_LOCKMGR': 9961472,
    'SI_SUB_VM': 16777216,
    'SI_SUB_KMEM': 25165824,
    'SI_SUB_KVM_RSRC': 27262976,
    'SI_SUB_WITNESS': 27787264,
    'SI_SUB_MTX_POOL_DYNAMIC': 28049408,
    'SI_SUB_LOCK': 28311552,
    'SI_SUB_EVENTHANDLER': 29360128,
    'SI_SUB_VNET_PRELINK': 31457280,
    'SI_SUB_KLD': 33554432,
    'SI_SUB_CPU': 34603008,
    'SI_SUB_RACCT': 34668544,
    'SI_SUB_RANDOM': 34734080,
    'SI_SUB_KDTRACE': 34865152,
    'SI_SUB_MAC': 35127296,
    'SI_SUB_MAC_POLICY': 35389440,
    'SI_SUB_MAC_LATE': 35454976,
    'SI_SUB_VNET': 35520512,
    'SI_SUB_INTRINSIC': 35651584,
    'SI_SUB_VM_CONF': 36700160,
    'SI_SUB_DDB_SERVICES': 37224448,
    'SI_SUB_RUN_QUEUE': 37748736,
    'SI_SUB_KTRACE': 38273024,
    'SI_SUB_OPENSOLARIS': 38338560,
    'SI_SUB_CYCLIC': 38404096,
    'SI_SUB_AUDIT': 38535168,
    'SI_SUB_CREATE_INIT': 38797312,
    'SI_SUB_SCHED_IDLE': 39845888,
    'SI_SUB_MBUF': 40894464,
    'SI_SUB_INTR': 41943040,
    'SI_SUB_SOFTINTR': 41943041,
    'SI_SUB_ACL': 42991616,
    'SI_SUB_DEVFS': 49283072,
    'SI_SUB_INIT_IF': 50331648,
    'SI_SUB_NETGRAPH': 50397184,
    'SI_SUB_DTRACE': 50462720,
    'SI_SUB_DTRACE_PROVIDER': 50626560,
    'SI_SUB_DTRACE_ANON': 50905088,
    'SI_SUB_DRIVERS': 51380224,
    'SI_SUB_CONFIGURE': 58720256,
    'SI_SUB_VFS': 67108864,
    'SI_SUB_CLOCKS': 75497472,
    'SI_SUB_CLIST': 92274688,
    'SI_SUB_SYSV_SHM': 104857600,
    'SI_SUB_SYSV_SEM': 109051904,
    'SI_SUB_SYSV_MSG': 113246208,
    'SI_SUB_P': 115343360,
    'SI_SUB_PSEUDO': 117440512,
    'SI_SUB_EXEC': 121634816,
    'SI_SUB_PROTO_BEGIN': 134217728,
    'SI_SUB_PROTO_IF': 138412032,
    'SI_SUB_PROTO_DOMAININIT': 140509184,
    'SI_SUB_PROTO_DOMAIN': 142606336,
    'SI_SUB_PROTO_IFATTACHDOMAIN': 142606337,
    'SI_SUB_PROTO_END': 150994943,
    'SI_SUB_KPROF': 150994944,
    'SI_SUB_KICK_SCHEDULER': 167772160,
    'SI_SUB_INT_CONFIG_HOOKS': 176160768,
    'SI_SUB_ROOT_CONF': 184549376,
    'SI_SUB_DUMP_CONF': 186646528,
    'SI_SUB_RAID': 188219392,
    'SI_SUB_SWAP': 201326592,
    'SI_SUB_INTRINSIC_POST': 218103808,
    'SI_SUB_SYSCALLS': 226492416,
    'SI_SUB_VNET_DONE': 230686720,
    'SI_SUB_KTHREAD_INIT': 234881024,
    'SI_SUB_KTHREAD_PAGE': 239075328,
    'SI_SUB_KTHREAD_VM': 243269632,
    'SI_SUB_KTHREAD_BUF': 245366784,
    'SI_SUB_KTHREAD_UPDATE': 247463936,
    'SI_SUB_KTHREAD_IDLE': 249561088,
    'SI_SUB_SMP': 251658240,
    'SI_SUB_RACCTD': 252706816,
    'SI_SUB_RUN_SCHEDULER': 268435455,
}

order_one['PFIL_SYSINIT_ORDER'] = order_one['SI_SUB_PROTO_BEGIN']


order_two = {
    "SI_ORDER_FIRST": 0,
    "SI_ORDER_SECOND": 1,
    "SI_ORDER_THIRD": 2,
    "SI_ORDER_FOURTH": 3,
    "SI_ORDER_MIDDLE": 16777216,
    "SI_ORDER_ANY": 268435455,
}

order_two["PFIL_VNET_ORDER"] = order_two["SI_ORDER_FIRST"] + 2

matches = []

def extract_matches(mt):
    global order_one
    global order_two
    global matches

    for m in mt:
        l = [x.strip() for x in m]
        (name,o1,o2,func,udata) = l

        if (not order_one.has_key(o1)):
            print o1, "is not in order_one dict"
            sys.exit(1)

        if (not order_two.has_key(o2)):
            print o2, "is not in order_two dict"
            sys.exit(1)

        matches += [["%s(%s);" % (func, udata), order_one[o1], order_two[o2]]]
   
def handle_file(fname):

    # Extract SYSINIT and VNET_SYSINIT macro variables from file
    txt = file(fname).read()
    f = re.findall("^VNET_SYSINIT\((.*?),(.*?),(.*?),(.*?),(.*?)\)", txt, re.I + re.M + re.S)
    g = re.findall("^SYSINIT\((.*?),(.*?),(.*?),(.*?),(.*?)\)", txt, re.I + re.M + re.S)
    
    extract_matches(f)
    extract_matches(g)

def process_files(top):

    for root, dirs, files in os.walk(top):

        # include files
        files = [os.path.join(root, f) for f in files]
        files = [f for f in files if re.match(includes, f)]

        for fname in files:
            handle_file(fname)

#
# MAIN
#

if (__name__ == "__main__"):

    # Extract matches from the bsd tree
    process_files(sys.argv[1])

    # Order matches
    matches.sort(key = lambda o: o[1]*(2**32) + o[2])
    print "Debug Print:"
    for o in matches:
        print "%s    %s,%s" % (o[0], hex(o[1]), hex(o[2]))

    print "\nCopy & Paste Me:"
    for o in matches:
        print o[0]

    
