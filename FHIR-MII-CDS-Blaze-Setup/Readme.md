# Blaze instance deployment

1. Install docker and docker-compose extension according to your system
2. Ensure you installed docker accordingly (```docker run hello-world``` should work as intended)
3. Start the Blaze instance via ```./start_blaze.sh``` (Ensure you set execution permissions for the ```.sh``` files)
4. The instance should start successfully and should be available via ```http://localhost:8080```
5. Test if the instance is available executing ```curl http://localhost:8080/health``` (```OK``` expeceted)
6. Install blazectl