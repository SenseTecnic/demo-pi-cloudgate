=========================================
Configuring Raspberry Pi as a DHCP server
=========================================

To configure your raspberry pi for easy configuration you can use the following example configuration. First install DHCP server:

```
sudo apt-get install isc-dhcp-server
```

And edit the two following files:

```
sudo nano /etc/dhcp/dhcp.conf
sudo nano /etc/network/interfaces
```

Finally, restart the service:

```
sudo service isc-dhcpd-server stop
sudo service isc-dhcpd-server start
```

Read More
=========

A file called rpi_raspbianwheezy_dhcp_server.pdf has more information on how to configure your Raspberry Pi as a DHCP server.
