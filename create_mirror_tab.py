#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""

**Project Name:**      MakeHuman-Helpers

**Authors:**           Black Punkduck

**Code Home Page:**    https://github.com/black-punkduck/MakeHuman-Helpers

**Copyright(c):**      Black Punkduck

**Licensing:**         AGPL3

    This file is part of the MakeHuman Support Tools

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Abstract
--------
Helper to create a table with all vertex number and mirror vertices and orientation

"""

import re
import sys
import json
import argparse
import math

configfilename = "data/mh_helper.json"

parser = argparse.ArgumentParser(description='Create a table with all vertex number and mirror vertices and orientation. Maximum deviation is 0.05')
parser.add_argument('-b', default="", metavar='base_object', help='an optional base mesh in .obj format (default: see configuration)')
parser.add_argument('-m', default=0.05, metavar='MAXDIST', type=float,  help='maximum deviation allowed for being considered as a mirrored vertex. Should be lower than 0.05')
args = parser.parse_args()

mirror = {}

def GetMirrorVNum (x, y, z, m, eps):
    if (eps == 0):
        for vnum in mirror.keys():
            if mirror[vnum]["m"] == -1 and mirror[vnum]["x"] == -x and mirror[vnum]["y"] == y and mirror[vnum]["z"] ==  z:
                mirror[vnum]["m"] = m
                return (vnum)
    else:
        for vnum in mirror.keys():
            if mirror[vnum]["m"] == -1:
                dx = abs(mirror[vnum]["x"] + x)
                dy = abs(mirror[vnum]["y"] - y)
                dz = abs(mirror[vnum]["z"] - z)
                dist = math.sqrt (dx * dx + dy * dy + dz * dz)
                if dist <= eps:
                    mirror[vnum]["m"] = m
                    return (vnum)

    return (-1);



if len(args.b):
    meshfile = args.b
else:
    #
    # read configuration
    #
    cfile = open (configfilename, "r")
    config = json.load (cfile)
    cfile.close()
    meshfile = config["base_object"]


# read the object file
#
vnum = 0
with open(meshfile) as f:
    for line in f:
        m=re.search("^\s*v\s+(\S+)\s+(\S+)\s+(\S+)", line)
        if (m is not None):
            mirror[vnum] = { 'x': float(m.group(1)),'y': float(m.group(2)), 'z': float(m.group(3)), 'm': -1 }
            vnum += 1
    f.close()

print (str(vnum) + " vertices processed", file=sys.stderr)

# now calculate mirror

still_unmirrored = True
for eps in [0, 0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]:
    if still_unmirrored and eps <= args.m:
        print ("epsilon " + str(eps) + ": ",  file=sys.stderr, end='')
        sys.stderr.flush()

        unmirrored = 0
        for i in range (0, vnum):
            if mirror[i]["m"] == -1:
                mirror[i]["m"] = GetMirrorVNum ( mirror[i]["x"], mirror[i]["y"], mirror[i]["z"], i, eps)
                if ( mirror[i]["m"]  == -1):
                    unmirrored +=1 
        print (str(unmirrored) + " unmirrored vertices", file=sys.stderr)
        if unmirrored == 0:
            still_unmirrored = False


# print the result

for i in range (0, vnum):
    pos = 'l'
    if mirror[i]["m"] == i:
        pos = 'm'
    elif mirror[i]["x"] < 0:
         pos = 'r'
    print (str(i) + " " + str(mirror[i]["m"]) + " " + pos )

exit (0)
