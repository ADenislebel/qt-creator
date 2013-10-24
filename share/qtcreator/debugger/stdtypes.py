############################################################################
#
# Copyright (C) 2013 Digia Plc and/or its subsidiary(-ies).
# Contact: http://www.qt-project.org/legal
#
# This file is part of Qt Creator.
#
# Commercial License Usage
# Licensees holding valid commercial Qt licenses may use this file in
# accordance with the commercial license agreement provided with the
# Software or, alternatively, in accordance with the terms contained in
# a written agreement between you and Digia.  For licensing terms and
# conditions see http://qt.digia.com/licensing.  For further information
# use the contact form at http://qt.digia.com/contact-us.
#
# GNU Lesser General Public License Usage
# Alternatively, this file may be used under the terms of the GNU Lesser
# General Public License version 2.1 as published by the Free Software
# Foundation and appearing in the file LICENSE.LGPL included in the
# packaging of this file.  Please review the following information to
# ensure the GNU Lesser General Public License version 2.1 requirements
# will be met: http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
#
# In addition, as a special exception, Digia gives you certain additional
# rights.  These rights are described in the Digia Qt LGPL Exception
# version 1.1, included in the file LGPL_EXCEPTION.txt in this package.
#
#############################################################################

from dumper import *

def qdump____c_style_array__(d, value):
    type = value.type.unqualified()
    targetType = value[0].type
    #d.putAddress(value.address)
    d.putType(type)
    d.putNumChild(1)
    format = d.currentItemFormat()
    isDefault = format == None and str(targetType.unqualified()) == "char"
    if isDefault or format == 0 or format == 1 or format == 2:
        blob = d.readMemory(d.addressOf(value), type.sizeof)

    if isDefault:
        # Use Latin1 as default for char [].
        d.putValue(blob, Hex2EncodedLatin1)
    elif format == 0:
        # Explicitly requested Latin1 formatting.
        d.putValue(blob, Hex2EncodedLatin1)
    elif format == 1:
        # Explicitly requested UTF-8 formatting.
        d.putValue(blob, Hex2EncodedUtf8)
    elif format == 2:
        # Explicitly requested Local 8-bit formatting.
        d.putValue(blob, Hex2EncodedLocal8Bit)
    else:
        d.putValue("@0x%x" % d.pointerValue(value.cast(targetType.pointer())))

    if d.currentIName in d.expandedINames:
        p = d.addressOf(value)
        ts = targetType.sizeof
        if not d.tryPutArrayContents(targetType, p, int(type.sizeof / ts)):
            with Children(d, childType=targetType,
                    addrBase=p, addrStep=ts):
                d.putFields(value)


def qdump__std__array(d, value):
    size = d.numericTemplateArgument(value.type, 1)
    d.putItemCount(size)
    d.putNumChild(size)
    if d.isExpanded():
        innerType = d.templateArgument(value.type, 0)
        d.putArrayData(innerType, d.addressOf(value), size)


def qdump__std____1__array(d, value):
    qdump__std__array(d, value)


def qdump__std__complex(d, value):
    innerType = d.templateArgument(value.type, 0)
    base = value.address.cast(innerType.pointer())
    real = base.dereference()
    imag = (base + 1).dereference()
    d.putValue("(%f, %f)" % (real, imag));
    d.putNumChild(2)
    if d.isExpanded():
        with Children(d, 2, childType=innerType):
            d.putSubItem("real", real)
            d.putSubItem("imag", imag)


def qdump__std__deque(d, value):
    innerType = d.templateArgument(value.type, 0)
    innerSize = innerType.sizeof
    bufsize = 1
    if innerSize < 512:
        bufsize = int(512 / innerSize)

    impl = value["_M_impl"]
    start = impl["_M_start"]
    finish = impl["_M_finish"]
    size = bufsize * toInteger(finish["_M_node"] - start["_M_node"] - 1)
    size += toInteger(finish["_M_cur"] - finish["_M_first"])
    size += toInteger(start["_M_last"] - start["_M_cur"])

    d.check(0 <= size and size <= 1000 * 1000 * 1000)
    d.putItemCount(size)
    d.putNumChild(size)
    if d.isExpanded():
        with Children(d, size, maxNumChild=2000, childType=innerType):
            pcur = start["_M_cur"]
            pfirst = start["_M_first"]
            plast = start["_M_last"]
            pnode = start["_M_node"]
            for i in d.childRange():
                d.putSubItem(i, pcur.dereference())
                pcur += 1
                if pcur == plast:
                    newnode = pnode + 1
                    pnode = newnode
                    pfirst = newnode.dereference()
                    plast = pfirst + bufsize
                    pcur = pfirst

def qdump__std____debug__deque(d, value):
    qdump__std__deque(d, value)


def qdump__std__list(d, value):
    head = d.dereferenceValue(value)
    impl = value["_M_impl"]
    node = impl["_M_node"]
    size = 0
    pp = d.dereference(head)
    while head != pp and size <= 1001:
        size += 1
        pp = d.dereference(pp)

    d.putItemCount(size, 1000)
    d.putNumChild(size)

    if d.isExpanded():
        p = node["_M_next"]
        innerType = d.templateArgument(value.type, 0)
        with Children(d, size, maxNumChild=1000, childType=innerType):
            for i in d.childRange():
                innerPointer = innerType.pointer()
                d.putSubItem(i, (p + 1).cast(innerPointer).dereference())
                p = p["_M_next"]

def qdump__std____debug__list(d, value):
    qdump__std__list(d, value)

def qform__std__map():
    return mapForms()

def qdump__std__map(d, value):
    impl = value["_M_t"]["_M_impl"]
    size = int(impl["_M_node_count"])
    d.check(0 <= size and size <= 100*1000*1000)
    d.putItemCount(size)
    d.putNumChild(size)

    if d.isExpanded():
        keyType = d.templateArgument(value.type, 0)
        valueType = d.templateArgument(value.type, 1)
        try:
            # Does not work on gcc 4.4, the allocator type (fourth template
            # argument) seems not to be available.
            pairType = d.templateArgument(d.templateArgument(value.type, 3), 0)
            pairPointer = pairType.pointer()
        except:
            # So use this as workaround:
            pairType = d.templateArgument(impl.type, 1)
            pairPointer = pairType.pointer()
        isCompact = d.isMapCompact(keyType, valueType)
        innerType = pairType
        if isCompact:
            innerType = valueType
        node = impl["_M_header"]["_M_left"]
        childType = innerType
        if size == 0:
            childType = pairType
        childNumChild = 2
        if isCompact:
            childNumChild = None
        with Children(d, size, maxNumChild=1000,
                childType=childType, childNumChild=childNumChild):
            for i in d.childRange():
                with SubItem(d, i):
                    pair = (node + 1).cast(pairPointer).dereference()
                    if isCompact:
                        d.putMapName(pair["first"])
                        d.putItem(pair["second"])
                    else:
                        d.putEmptyValue()
                        if d.isExpanded():
                            with Children(d, 2):
                                d.putSubItem("first", pair["first"])
                                d.putSubItem("second", pair["second"])
                if d.isNull(node["_M_right"]):
                    parent = node["_M_parent"]
                    while node == parent["_M_right"]:
                        node = parent
                        parent = parent["_M_parent"]
                    if node["_M_right"] != parent:
                        node = parent
                else:
                    node = node["_M_right"]
                    while not d.isNull(node["_M_left"]):
                        node = node["_M_left"]

def qdump__std____debug__map(d, value):
    qdump__std__map(d, value)

def qdump__std____debug__set(d, value):
    qdump__std__set(d, value)

def qdump__std____cxx1998__map(d, value):
    qdump__std__map(d, value)

def stdTreeIteratorHelper(d, value):
    node = value["_M_node"].dereference()
    d.putNumChild(1)
    d.putEmptyValue()
    if d.isExpanded():
        nodeTypeName = str(value.type).replace("_Rb_tree_iterator", "_Rb_tree_node", 1)
        nodeTypeName = nodeTypeName.replace("_Rb_tree_const_iterator", "_Rb_tree_node", 1)
        nodeType = d.lookupType(nodeTypeName)
        data = node.cast(nodeType)["_M_value_field"]
        with Children(d):
            try:
                d.putSubItem("first", data["first"])
                d.putSubItem("second", data["second"])
            except:
                d.putSubItem("value", data)
            with SubItem(d, "node"):
                d.putNumChild(1)
                d.putEmptyValue()
                d.putType(" ")
                if d.isExpanded():
                    with Children(d):
                        d.putSubItem("color", node["_M_color"])
                        d.putSubItem("left", node["_M_left"])
                        d.putSubItem("right", node["_M_right"])
                        d.putSubItem("parent", node["_M_parent"])


def qdump__std___Rb_tree_iterator(d, value):
    stdTreeIteratorHelper(d, value)

def qdump__std___Rb_tree_const_iterator(d, value):
    stdTreeIteratorHelper(d, value)

def qdump__std__map__iterator(d, value):
    stdTreeIteratorHelper(d, value)

def qdump____gnu_debug___Safe_iterator(d, value):
    d.putItem(value["_M_current"])

def qdump__std__map__const_iterator(d, value):
    stdTreeIteratorHelper(d, value)

def qdump__std__set__iterator(d, value):
    stdTreeIteratorHelper(d, value)

def qdump__std__set__const_iterator(d, value):
    stdTreeIteratorHelper(d, value)

def qdump__std____cxx1998__set(d, value):
    qdump__std__set(d, value)

def qdump__std__set(d, value):
    impl = value["_M_t"]["_M_impl"]
    size = int(impl["_M_node_count"])
    d.check(0 <= size and size <= 100*1000*1000)
    d.putItemCount(size)
    d.putNumChild(size)
    if d.isExpanded():
        valueType = d.templateArgument(value.type, 0)
        node = impl["_M_header"]["_M_left"]
        with Children(d, size, maxNumChild=1000, childType=valueType):
            for i in d.childRange():
                d.putSubItem(i, (node + 1).cast(valueType.pointer()).dereference())
                if d.isNull(node["_M_right"]):
                    parent = node["_M_parent"]
                    while node == parent["_M_right"]:
                        node = parent
                        parent = parent["_M_parent"]
                    if node["_M_right"] != parent:
                        node = parent
                else:
                    node = node["_M_right"]
                    while not d.isNull(node["_M_left"]):
                        node = node["_M_left"]


def qdump__std__stack(d, value):
    qdump__std__deque(d, value["c"])

def qdump__std____debug__stack(d, value):
    qdump__std__stack(d, value)

def qform__std__string():
    return "Inline,In Separate Window"

def qdump__std__string(d, value):
    qdump__std__stringHelper1(d, value, 1)

def qdump__std__stringHelper1(d, value, charSize):
    data = value["_M_dataplus"]["_M_p"]
    # We can't lookup the std::string::_Rep type without crashing LLDB,
    # so hard-code assumption on member position
    # struct { size_type _M_length, size_type _M_capacity, int _M_refcount; }
    sizePtr = data.cast(d.sizetType().pointer())
    size = int(sizePtr[-3])
    alloc = int(sizePtr[-2])
    refcount = int(sizePtr[-1])
    d.check(refcount >= -1) # Can be -1 accoring to docs.
    d.check(0 <= size and size <= alloc and alloc <= 100*1000*1000)
    qdump_stringHelper(d, sizePtr, size * charSize, charSize)

def qdump_stringHelper(d, data, size, charSize):
    cutoff = min(size, qqStringCutOff)
    mem = d.readMemory(data, cutoff)
    if charSize == 1:
        encodingType = Hex2EncodedLatin1
        displayType = DisplayLatin1String
    elif charSize == 2:
        encodingType = Hex4EncodedLittleEndian
        displayType = DisplayUtf16String
    else:
        encodingType = Hex8EncodedLittleEndian
        displayType = DisplayUtf16String

    d.putNumChild(0)
    d.putValue(mem, encodingType)

    format = d.currentItemFormat()
    if format == 1:
        d.putDisplay(StopDisplay)
    elif format == 2:
        d.putField("editformat", displayType)
        d.putField("editvalue", d.readMemory(data, size))


def qdump__std____1__string(d, value):
    inner = d.childAt(d.childAt(value["__r_"]["__first_"], 0), 0)
    size = int(inner["__size_"])
    alloc = int(inner["__cap_"])
    data = d.pointerValue(inner["__data_"])
    qdump_stringHelper(d, data, size, 1)
    d.putType("std::string")


def qdump__std____1__wstring(d, value):
    inner = d.childAt(d.childAt(value["__r_"]["__first_"], 0), 0)
    size = int(inner["__size_"]) * 4
    alloc = int(inner["__cap_"])
    data = d.pointerValue(inner["__data_"])
    qdump_stringHelper(d, data, size, 4)
    d.putType("std::wstring")


def qdump__std__shared_ptr(d, value):
    i = value["_M_ptr"]
    if d.isNull(i):
        d.putValue("(null)")
        d.putNumChild(0)
        return

    if d.isSimpleType(d.templateArgument(value.type, 0)):
        d.putValue("%s @0x%x" % (i.dereference(), d.pointerValue(i)))
    else:
        i = expensiveDowncast(i)
        d.putValue("@0x%x" % d.pointerValue(i))

    d.putNumChild(3)
    with Children(d, 3):
        d.putSubItem("data", i)
        refcount = value["_M_refcount"]["_M_pi"]
        d.putIntItem("usecount", refcount["_M_use_count"])
        d.putIntItem("weakcount", refcount["_M_weak_count"])

def qdump__std____1__shared_ptr(d, value):
    i = value["__ptr_"]
    if d.isNull(i):
        d.putValue("(null)")
        d.putNumChild(0)
        return

    if d.isSimpleType(d.templateArgument(value.type, 0)):
        d.putValue("%s @0x%x" % (i.dereference().value, d.pointerValue(i)))
    else:
        d.putValue("@0x%x" % d.pointerValue(i))

    d.putNumChild(3)
    with Children(d, 3):
        d.putSubItem("data", i.dereference())
        d.putFields(value["__cntrl_"].dereference())
        #d.putIntItem("usecount", refcount["_M_use_count"])
        #d.putIntItem("weakcount", refcount["_M_weak_count"])

def qdump__std__unique_ptr(d, value):
    i = value["_M_t"]["_M_head_impl"]
    if d.isNull(i):
        d.putValue("(null)")
        d.putNumChild(0)
        return

    if d.isSimpleType(d.templateArgument(value.type, 0)):
        d.putValue("%s @0x%x" % (i.dereference(), d.pointerValue(i)))
    else:
        i = expensiveDowncast(i)
        d.putValue("@0x%x" % d.pointerValue(i))

    d.putNumChild(1)
    with Children(d, 1):
        d.putSubItem("data", i)

def qdump__std____1__unique_ptr(d, value):
    i = d.childAt(d.childAt(value["__ptr_"], 0), 0)
    if d.isNull(i):
        d.putValue("(null)")
        d.putNumChild(0)
        return

    if d.isSimpleType(d.templateArgument(value.type, 0)):
        d.putValue("%s @0x%x" % (i.dereference().value, d.pointerValue(i)))
    else:
        d.putValue("@0x%x" % d.pointerValue(i))

    d.putNumChild(1)
    with Children(d, 1):
        d.putSubItem("data", i.dereference())


def qform__std__unordered_map():
    return mapForms()

def qform__std____debug__unordered_map():
    return mapForms()

def qdump__std__unordered_map(d, value):
    try:
        size = value["_M_element_count"]
        start = value["_M_before_begin"]["_M_nxt"]
    except:
        size = value["_M_h"]["_M_element_count"]
        start = value["_M_h"]["_M_bbegin"]["_M_node"]["_M_nxt"]
    d.putItemCount(size)
    d.putNumChild(size)
    if d.isExpanded():
        p = d.pointerValue(start)
        keyType = d.templateArgument(value.type, 0)
        valueType = d.templateArgument(value.type, 1)
        allocatorType = d.templateArgument(value.type, 4)
        pairType = d.templateArgument(allocatorType, 0)
        ptrSize = d.ptrSize()
        if d.isMapCompact(keyType, valueType):
            with Children(d, size, childType=valueType):
                for i in d.childRange():
                    pair = d.createValue(p + ptrSize, pairType)
                    with SubItem(d, i):
                        d.putField("iname", d.currentIName)
                        d.putName("[%s] %s" % (i, pair["first"]))
                        d.putValue(pair["second"])
                    p = d.dereference(p)
        else:
            with Children(d, size, childType=pairType):
                for i in d.childRange():
                    d.putSubItem(i, d.createValue(p + ptrSize, pairType))
                    p = d.dereference(p)

def qdump__std____debug__unordered_map(d, value):
    qdump__std__unordered_map(d, value)

def qdump__std__unordered_set(d, value):
    try:
        size = value["_M_element_count"]
        start = value["_M_before_begin"]["_M_nxt"]
    except:
        size = value["_M_h"]["_M_element_count"]
        start = value["_M_h"]["_M_bbegin"]["_M_node"]["_M_nxt"]
    d.putItemCount(size)
    d.putNumChild(size)
    if d.isExpanded():
        p = d.pointerValue(start)
        valueType = d.templateArgument(value.type, 0)
        with Children(d, size, childType=valueType):
            ptrSize = d.ptrSize()
            for i in d.childRange():
                d.putSubItem(i, d.createValue(p + ptrSize, valueType))
                p = d.dereference(p)

def qform__std____1__unordered_map():
    return mapForms()

def qdump__std____1__unordered_map(d, value):
    n = toInteger(value["__table_"]["__p2_"]["__first_"])
    d.putItemCount(n)
    if d.isExpanded():
        with Children(d, 1):
            d.putFields(value)

def qdump__std____debug__unordered_set(d, value):
    qdump__std__unordered_set(d, value)


def qedit__std__vector(expr, value):
    values = value.split(',')
    n = len(values)
    ob = gdb.parse_and_eval(expr)
    innerType = d.templateArgument(ob.type, 0)
    cmd = "set $d = (%s*)calloc(sizeof(%s)*%s,1)" % (innerType, innerType, n)
    gdb.execute(cmd)
    cmd = "set {void*[3]}%s = {$d, $d+%s, $d+%s}" % (ob.address, n, n)
    gdb.execute(cmd)
    cmd = "set (%s[%d])*$d={%s}" % (innerType, n, value)
    gdb.execute(cmd)

def qdump__std__vector(d, value):
    impl = value["_M_impl"]
    type = d.templateArgument(value.type, 0)
    alloc = impl["_M_end_of_storage"]
    isBool = str(type) == 'bool'
    if isBool:
        start = impl["_M_start"]["_M_p"]
        finish = impl["_M_finish"]["_M_p"]
        # FIXME: 8 is CHAR_BIT
        storage = d.lookupType("unsigned long")
        storagesize = storage.sizeof * 8
        size = (finish - start) * storagesize
        size += impl["_M_finish"]["_M_offset"]
        size -= impl["_M_start"]["_M_offset"]
    else:
        start = impl["_M_start"]
        finish = impl["_M_finish"]
        size = finish - start

    d.check(0 <= size and size <= 1000 * 1000 * 1000)
    d.check(finish <= alloc)
    d.checkPointer(start)
    d.checkPointer(finish)
    d.checkPointer(alloc)

    d.putItemCount(size)
    d.putNumChild(size)
    if d.isExpanded():
        if isBool:
            with Children(d, size, maxNumChild=10000, childType=type):
                for i in d.childRange():
                    q = start + int(i / storagesize)
                    d.putBoolItem(str(i), (q.dereference() >> (i % storagesize)) & 1)
        else:
            d.putArrayData(type, start, size)

def qdump__std____1__vector(d, value):
    innerType = d.templateArgument(value.type, 0)
    if d.isLldb and d.childAt(value, 0).type == innerType:
        # That's old lldb automatically formatting
        begin = d.dereferenceValue(value)
        size = value.GetNumChildren()
    else:
        # Normal case
        begin = d.pointerValue(value['__begin_'])
        end = d.pointerValue(value['__end_'])
        size = (end - begin) / innerType.sizeof

    d.putItemCount(size)
    d.putNumChild(size)
    if d.isExpanded():
        d.putArrayData(innerType, begin, size)


def qdump__std____debug__vector(d, value):
    qdump__std__vector(d, value)

def qedit__std__string(expr, value):
    cmd = "print (%s).assign(\"%s\")" % (expr, value)
    gdb.execute(cmd)

def qedit__string(expr, value):
    qedit__std__string(expr, value)

def qdump__string(d, value):
    qdump__std__string(d, value)

def qdump__std__wstring(d, value):
    charSize = d.lookupType('wchar_t').sizeof
    qdump__std__stringHelper1(d, value, charSize)

def qdump__std__basic_string(d, value):
    innerType = d.templateArgument(value.type, 0)
    qdump__std__stringHelper1(d, value, innerType.sizeof)

def qdump__wstring(d, value):
    qdump__std__wstring(d, value)


def qdump____gnu_cxx__hash_set(d, value):
    ht = value["_M_ht"]
    size = int(ht["_M_num_elements"])
    d.check(0 <= size and size <= 1000 * 1000 * 1000)
    d.putItemCount(size)
    d.putNumChild(size)
    type = d.templateArgument(value.type, 0)
    d.putType("__gnu__cxx::hash_set<%s>" % type)
    if d.isExpanded():
        with Children(d, size, maxNumChild=1000, childType=type):
            buckets = ht["_M_buckets"]["_M_impl"]
            bucketStart = buckets["_M_start"]
            bucketFinish = buckets["_M_finish"]
            p = bucketStart
            itemCount = 0
            for i in xrange(toInteger(bucketFinish - bucketStart)):
                if not d.isNull(p.dereference()):
                    cur = p.dereference()
                    while not d.isNull(cur):
                        with SubItem(d, itemCount):
                            d.putValue(cur["_M_val"])
                            cur = cur["_M_next"]
                            itemCount += 1
                p = p + 1


def qdump__uint8_t(d, value):
    d.putNumChild(0)
    d.putValue(int(value))

def qdump__int8_t(d, value):
    d.putNumChild(0)
    d.putValue(int(value))

