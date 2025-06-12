// Copyright 2022-2024 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//      http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package eu.teraflow.tid.bgp4Peer.peer;

import eu.teraflow.tid.bgp4Peer.bgp4session.BGP4PeerInitiatedSession;
import eu.teraflow.tid.bgp4Peer.bgp4session.BGP4SessionsInformation;
import eu.teraflow.tid.bgp4Peer.updateTEDB.UpdateDispatcher;
import eu.teraflow.tid.tedb.TEDB;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.Inet4Address;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.LinkedList;

public class BGP4SessionServerManager implements Runnable {
	private BGP4PeerInitiatedSession bgp4SessionServer;
	private Logger log;
	BGP4SessionsInformation bgp4SessionsInformation;
	int bgp4Port;
	private int holdTime;
	private int keepAliveTimer;
	private Inet4Address BGPIdentifier;
	private int version = 4;
	private int myAutonomousSystem;
	private boolean noDelay;
	private boolean isTest=false;
	private  TEDB tedb;
	private UpdateDispatcher ud;
	Inet4Address localBGP4Address; 
	private Boolean updateFrom;
	private Boolean sendTo;
	
	private LinkedList<BGP4LSPeerInfo> peersToConnect;
	
	public BGP4SessionServerManager(BGP4SessionsInformation bgp4SessionInformation, TEDB tedb,UpdateDispatcher ud, int bgp4Port,int holdTime,Inet4Address BGPIdentifier,int version,int myAutonomousSystem,boolean noDelay,Inet4Address localAddress ,int mykeepAliveTimer, LinkedList<BGP4LSPeerInfo> peersToConnect ){
		log = LoggerFactory.getLogger("BGP4Peer");
		this.holdTime=holdTime;
		this.BGPIdentifier=BGPIdentifier;
		this.version = version;
		this.myAutonomousSystem=myAutonomousSystem;
		this.bgp4SessionsInformation=bgp4SessionInformation;
		this.bgp4Port=bgp4Port;
		this.noDelay=noDelay;
		this.tedb=tedb;
		this.ud=ud;
		this.localBGP4Address=localAddress;
		this.keepAliveTimer = mykeepAliveTimer;
		this.peersToConnect=peersToConnect;
	}

	public BGP4SessionServerManager(BGP4SessionsInformation bgp4SessionInformation, TEDB tedb,UpdateDispatcher ud, int bgp4Port,int holdTime,Inet4Address BGPIdentifier,int version,int myAutonomousSystem,boolean noDelay,Inet4Address localAddress ,int mykeepAliveTimer, LinkedList<BGP4LSPeerInfo> peersToConnect, boolean test){
		log = LoggerFactory.getLogger("BGP4Peer");
		this.holdTime=holdTime;
		this.BGPIdentifier=BGPIdentifier;
		this.version = version;
		this.myAutonomousSystem=myAutonomousSystem;
		this.bgp4SessionsInformation=bgp4SessionInformation;
		this.bgp4Port=bgp4Port;
		this.noDelay=noDelay;
		this.tedb=tedb;
		this.ud=ud;
		this.localBGP4Address=localAddress;
		this.keepAliveTimer = mykeepAliveTimer;
		this.peersToConnect=peersToConnect;
		this.isTest=test;
	}


	public Boolean getSendTo() {
		return sendTo;
	}

	public void setSendTo(Boolean sendTo) {
		this.sendTo = sendTo;
	}
	
	public Boolean getUpdateFrom() {
		return updateFrom;
	}

	public void setUpdateFrom(Boolean updateFrom) {
		this.updateFrom = updateFrom;
	}

	@Override
	public void run() {

		

		ServerSocket serverSocket = null;
		boolean listening = true;
		try {
			log.debug("SERVER Listening on port: "+ bgp4Port);
			log.debug("SERVER Listening on address: "+ localBGP4Address);
			serverSocket = new ServerSocket( bgp4Port,0,localBGP4Address);
		} catch (IOException e) {
			log.error("Could not listen on port: "+ bgp4Port);
			System.exit(-1);
		}
		while (listening) {	
			try {
				Socket sock=serverSocket.accept();
				bgp4SessionServer = new BGP4PeerInitiatedSession(sock,bgp4SessionsInformation,ud,holdTime,BGPIdentifier,version,myAutonomousSystem,noDelay,keepAliveTimer);
				if (isTest){
					log.info("isTest");
					bgp4SessionServer.setSendTo(true);
					bgp4SessionServer.start();
				}
				else {
					log.info("Not Test");
					for (int i = 0; i < this.peersToConnect.size(); i++) {
						try {
							Inet4Address add = peersToConnect.get(i).getPeerIP();
							if (add == null) {
								log.warn("peer IP address shouldn't be null");
							} else {
								if (add.equals(sock.getInetAddress())) {
									log.debug("FOUND " + add);
									bgp4SessionServer.setSendTo(this.peersToConnect.get(i).isSendToPeer());
								}
							}

						} catch (Exception e) {
							e.printStackTrace();
						}

					}
					bgp4SessionServer.start();
				}
			}catch (Exception e) {
				e.printStackTrace();
			}
		}
		try {
			log.info("Closing the socket");
			serverSocket.close();
		
		}catch (Exception e) {
				e.printStackTrace();
		}

	}

}
