Overview
========

This Dag pulls connections from current airflow environment and pushes them to an Astronomer deployment. This can be run from an Astronomer Local Dev environomet or any other Airflow deployment to move connections into Astro

How to setup
================
Create Airflow Variables with the following Keys:
- ASTRO_URL - Open Airflow via Astronomer and copy the URL, you will need to remove the /home . EX:https://company.astronomer.run/xxxxxxxx
- ASTRO_ACCESS_KEY - Go to https://cloud.astronomer.io/token after logging into Astronomer. 
This will create a token that is valid for only 24 hours. Copy the supplied token into the Astronomer Variable

Install the `requests` python library. If you are using an Astronomer local Developer environment this can be done by adding `requests` to your requirements.txt

How to Run
===========================
Simple run the included DAG and ensure the task run successfully

Verify
=================================

Check that the connections are in you Astro instance by Going to Airflow Admin -> Connections  and make sure all the connections are listed there. 

If the DAG does not run successfully make sure you delete the created Xcoms, as they potentionally contain passwords. If everything runs correctly passwords should be deleted, but please verify by checking you Xcoms
