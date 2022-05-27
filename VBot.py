# -*- coding: utf-8 -*- 
from multiprocessing.sharedctypes import Value
import time
from CHRLINE import *
from CHRLINE.hooks import HooksTracer
import requests
import json


cl = CHRLINE("username", "password")
# ...
# cl8 = CHRLINE()

tracer = HooksTracer(
    cl, # main account
    prefixes=["/"], # cmd prefixes
    # db="test_hook", # database name, if None will use main account's mid
    # accounts=[cl8] # sub accounts
)

ADMINS = [] # admin's mids
for _admin in ADMINS:
    tracer.addPermission(_admin, 'admin') # add permission to db

class EventHook:

    @tracer.Event
    def onReady():
        print('Ready!')

class OpHook(object):

    @tracer.Operation(25)
    def sendMessage(self, op, cl):
        msg = op[20]
        pass

    @tracer.Operation(26)
    def recvMessage(self, op, cl):
        msg = op[20]
        #if msg[1] == cl8.mid:
        #    return # pass if is bot message
        self.trace(msg, self.HooksType["Content"], cl)

    @tracer.Operation(124)
    def recvChatInvite(self, op, cl):
        gid = op[10]
        inviter = op[11]
        mid = op[12]
        if mid == cl.mid:
            # someone invited the bot
            cl.acceptChatInvitation(gid) # join

    @tracer.Operation(127)
    def deleteSelfFromChat(self, op, cl):
        gid = op[10]
        if gid in cl.groups:
            cl.groups.remove(gid) # update local cache data

    @tracer.Operation(129)
    def joinChat(self, op, cl):
        gid = op[10]
        if gid not in cl.groups:
            cl.groups.append(gid) # update local cache data

    @tracer.Operation(133)
    def recvDeleteOtherFromChat(self, op, cl):
        gid = op[10]
        kicker = op[11]
        mid = op[12]
        if mid == cl.mid:
            # someone kick the bot
            if gid in cl.groups:
                cl.groups.remove(gid) # update local cache data

    @tracer.Before(tracer.HooksType["Operation"])
    def __before(self, op, cl):
        # handle all op
        # u can do something here for the same operation when multiple accounts
        pass

    @tracer.After(tracer.HooksType["Operation"])
    def __after(self, op, cl):
        # handle not tracked op
        opType = op[3]
        if opType not in [0, 48]:
            print(f"[{op[3]}]{op}")

class ContentHook(object):

    @tracer.Content(0)
    def TextMessage(self, msg, cl):
        text = msg.get(10)
        self.trace(msg, self.HooksType['Command'], cl)

    @tracer.Content(1)
    def ImageMessage(self, msg, cl):
        id = msg[4]
        metadata = msg[18]

class NormalCmd(object):

    @tracer.Command(ignoreCase=True)
    def hi(self, msg, cl):
        '''Debug.'''
        cl.replyMessage(msg, "Hi!")

    @tracer.Command(ignoreCase=True, inpart=True)
    def test(self, msg, cl):
        '''Test.'''
        cl.replyMessage(msg, "this is test!")

    @tracer.Command(alt=["指令"], ignoreCase=True)
    def help(self, msg, cl):
        '''cmd list'''
        cl.replyMessage(msg, self.genHelp(self.getPrefix(msg[10])))

    @tracer.Command(alt=["sp"], ignoreCase=True)
    def speed(self, msg, cl):
        '''測速用'''
        a = time.time()
        cl.replyMessage(msg, 'okok...')
        b = time.time() - a
        cl.replyMessage(msg, f'speed: {b}s')

    @tracer.Command(ignoreCase=True, inpart=True)
    def mid(self, msg, cl):
        '''查詢 mid'''
        mid = self.getArgs(msg[10], defVal=msg[1])[0]
        mentionees = cl.getMentioneesByMsgData(msg)
        if not mentionees:
            cl.replyMessage(msg, msg[1])
        else:
            mentions = []
            reply = ''
            # TODO: 
            #   - mentions
            for mention_mid in mentionees:
                membername = cl.getContact(mention_mid)
                membername = membername[22]
                reply += f'{membername}\n{mention_mid}\n'
            try:
                cl.sendMessageWithE2EE(mid, reply) # or sendCompactE2EEMessage
            except:
                cl.sendMessage(mid, reply) # or sendCompactMessage

    @tracer.Command(permissions=["admin"], ignoreCase=True)
    def checkOp(self, msg, cl):
        '''Admin Only.'''
        cl.replyMessage(msg, f'u is Admin!')

    @tracer.Command(ignoreCase=True)
    def getOp(self, msg, cl):
        '''get Admin!'''
        reply = "You are already an admin!"
        if self.addPermission(msg[1], 'admin'):
            reply = "You are now admin!"
        cl.replyMessage(msg, reply)

    @tracer.Command(ignoreCase=True)
    def ops(self, msg, cl):
        '''Admin List.'''
        al = self.getPermission('admin')
        reply = ''
        if al:
            for am in al:
                reply += f'- {am[:6]}\n'
            reply += f"Total: {len(al)}" 
        else:
            reply = 'No Admin'
        cl.replyMessage(msg, reply)

    @tracer.Command(ignoreCase=True, toType=[2]) # toType 指定
    def bye(self, msg, cl):
        '''byebye'''
        
        cl.deleteSelfFromChat(msg[2])

    @tracer.Command(ignoreCase=True) # toType 指定
    def getgrouplist(self, msg, cl):
        '''Get Group Member List'''
        
        membername = []
        membermid = []
        chatinfo = cl.getChats([msg[2]])
        groupname = chatinfo[1][0][6]
        chatinfo = chatinfo[1][0][8][1][4]

        members = list(chatinfo.keys())
        # print(members)
        # reply = cl.getContacts(self, members)
        print("Updating Group List... (" + groupname + ")")
        if(len(members) > 250):
            middle = len(members) // 2
            members_first = members[:middle]
            members_second = members[middle:] 
            contactinfo = cl.getContacts(members_first)
            for memberinfo in contactinfo:
                membername.append(memberinfo[22])
                membermid.append(memberinfo[1])
            contactinfo = cl.getContacts(members_second)
            for memberinfo in contactinfo:
                membername.append(memberinfo[22])
                membermid.append(memberinfo[1])
        else:
            contactinfo = cl.getContacts(members)
            for memberinfo in contactinfo:
                membername.append(memberinfo[22])
                membermid.append(memberinfo[1])

        url = ''    # Google script url
        payload = {}
        payload['groupname'] = groupname
        payload['members'] = membername
        payload['mids'] = membermid
        payloadjson = json.dumps(payload)
        r = requests.post(url, data=payloadjson)
        if r.status_code == requests.codes.ok:
            print("Update Member List Success! (" + groupname + ")")
        else :
            print("Update Member List Failed! (" + groupname + ")")

    @tracer.Command(ignoreCase=True, splitchar=":")
    def pm(self, msg, cl):
        '''priv msg for test E2EE'''
        mid = self.getArgs(msg[10], defVal=msg[1])[0]
        try:
            cl.sendMessageWithE2EE(mid, 'hello') # or sendCompactE2EEMessage
        except:
            cl.sendMessage(mid, 'hello') # or sendCompactMessage

tracer.run()