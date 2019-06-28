import threading
import socket

# usage:
# server=EdgeServer.SocketServer()
# server.setInit([],'192.168.3.66',5678)
# # server.run2(server.actionsend,'192.168.3.67')
# server.run(server.actionbroadcast)

class SocketServer():
    _instance_lock=threading.Lock()#进程锁，创建单例模式

    def __new__(cls, *args, **kwargs):
        if not hasattr(SocketServer, "_instance"):
            with SocketServer._instance_lock:
                if not hasattr(SocketServer, "_instance"):
                    SocketServer._instance = object.__new__(cls)  
        return SocketServer._instance

    def __init__(self):
        pass

    def setInit(self,socket_list,ip,port):
        super().__init__()
        self.socket_list=socket_list
        self.ip=ip
        self.port=port
 
    def run(self,action):
        sock = socket.socket()
        sock.bind((self.ip, self.port))
        sock.listen(5)
        print("Start listen:"+str(self.port))
        while True:
            conn, addr = sock.accept()
            print("Connect by", addr)
            self.socket_list.append((conn, addr))
            
            threading.Thread(target=action,args=(conn,addr,)).start()

    def run2(self,action,ip):
        sock = socket.socket()
        sock.bind((self.ip, self.port))
        sock.listen(5)
        print("Start listen:"+str(self.port))
        while True:
            conn, addr = sock.accept()
            print("Connect by", addr)
            self.socket_list.append((conn, addr))
            
            threading.Thread(target=action,args=(conn,addr,ip,)).start()

    def broadcast(self,msgbytes):
        for sock,addr in self.socket_list:
            try:
                sock.sendall(msgbytes)
            except:
                print("except by:",addr)
                self.socket_list.remove((sock,addr))
    
    def send(self,msgbytes,ip):
        for sock,addr in self.socket_list:
            try:
                if addr[0]==ip:
                    sock.sendall(msgbytes)
            except:
                print("send except by:",addr)
                self.socket_list.remove((sock,addr))

    def wakeup(self,mac):
        packet=binascii.unhexlify('FF'*6+mac*16)
        #print(packet)
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)#UDP broadcast
        s.sendto(packet,(broadcastip,9))
        s.close()

    def actionbroadcast(self,conn,addr):
        "broadcast msg to every socket in list"
        while True:
            try:
                data=conn.recv(1024)
                if not data:
                    break
                print(str(addr)+'发送来的数据：',data)
                SocketServer().broadcast(data)

            except NameError as err:
                print("action except by:",str(err))
            except ConnectionResetError as err:
                print("ConnectionResetError:",str(err))
                break
        print("conn %s closed."%addr[0])
        conn.close()
        self.socket_list.remove((conn,addr))
        print(self.socket_list)

    def actionsend(self,conn,addr,ip):
        "change send msg to ip"
        while True:
            try:
                data=conn.recv(1024)
                if not data:
                    break
                print(str(addr)+'发送来的数据：',data)
                SocketServer().send(data,ip)

            except NameError as err:
                print("action except by:",str(err))
            except ConnectionResetError as err:
                print("ConnectionResetError:",str(err))
                break
        print("conn %s closed."%addr[0])
        conn.close()
        self.socket_list.remove((conn,addr))
        print(self.socket_list)