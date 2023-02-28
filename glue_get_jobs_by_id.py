import boto3

def get_glue_status(jobname, runid):
    client = boto3.client('glue')
    '''
    response = client.get_job_runs(
        JobName=jobname,
        #NextToken='string',
        MaxResults=123
    )
    '''
    response = client.get_job_run(
        JobName=jobname,
        RunId=runid,
        PredecessorsIncluded=True
    )
    for item in response['JobRuns']:
        if item['Id'] = runid:
            status = item['JobRunState']
            emessage = item['ErrorMessage']
    return status, emessage
