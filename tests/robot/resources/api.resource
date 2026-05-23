*** Settings ***
Library           Collections
Library           DateTime
Library           OperatingSystem
Library           Process
Library           RequestsLibrary

*** Variables ***
${BASE_URL}       http://127.0.0.1:8000
${API_ALIAS}      ecom_api

*** Keywords ***
Prepare API Session
    Reset Database To Known State
    Create Session    ${API_ALIAS}    ${BASE_URL}
    API Should Be Healthy

Close API Session
    Delete All Sessions

Reset Database To Known State
    ${project_root}=    Normalize Path    ${CURDIR}/../../..
    ${venv_python}=    Normalize Path    ${project_root}/.venv/bin/python
    ${has_venv_python}=    Run Keyword And Return Status    File Should Exist    ${venv_python}
    ${python_executable}=    Set Variable If    ${has_venv_python}    ${venv_python}    python
    ${seed_result}=    Run Process    ${python_executable}    -m    utils.seed_database    cwd=${project_root}    stderr=STDOUT
    Log    ${seed_result.stdout}
    Should Be Equal As Integers    ${seed_result.rc}    0

API Should Be Healthy
    ${response}=    GET On Session    ${API_ALIAS}    /
    Should Be Equal As Integers    ${response.status_code}    200
    ${body}=    Evaluate    $response.json()
    Dictionary Should Contain Item    ${body}    message    Hello There!!

Get Collection By Endpoint
    [Arguments]    ${endpoint}
    ${response}=    GET On Session    ${API_ALIAS}    ${endpoint}
    Should Be Equal As Integers    ${response.status_code}    200
    ${items}=    Evaluate    $response.json()
    RETURN    ${items}

Find Item By Field
    [Arguments]    ${endpoint}    ${field_name}    ${field_value}
    @{items}=    Get Collection By Endpoint    ${endpoint}
    FOR    ${item}    IN    @{items}
        ${candidate}=    Get From Dictionary    ${item}    ${field_name}
        IF    '${candidate}' == '${field_value}'
            RETURN    ${item}
        END
    END
    Fail    Item with ${field_name}=${field_value} was not found in ${endpoint}

Get Resource By Id
    [Arguments]    ${endpoint}    ${resource_id}
    ${response}=    GET On Session    ${API_ALIAS}    ${endpoint}/${resource_id}
    Should Be Equal As Integers    ${response.status_code}    200
    ${body}=    Evaluate    $response.json()
    RETURN    ${body}

Create Resource
    [Arguments]    ${endpoint}    &{payload}
    ${response}=    POST On Session    ${API_ALIAS}    ${endpoint}    json=${payload}
    Should Be Equal As Integers    ${response.status_code}    201
    ${body}=    Evaluate    $response.json()
    RETURN    ${body}

Create Resource Expecting Conflict
    [Arguments]    ${endpoint}    &{payload}
    ${response}=    POST On Session    ${API_ALIAS}    ${endpoint}    json=${payload}    expected_status=any
    Should Be Equal As Integers    ${response.status_code}    409

Delete Resource
    [Arguments]    ${endpoint}    ${resource_id}
    ${response}=    DELETE On Session    ${API_ALIAS}    ${endpoint}/${resource_id}
    Should Be Equal As Integers    ${response.status_code}    204

Delete Resource Expecting Conflict
    [Arguments]    ${endpoint}    ${resource_id}
    ${response}=    DELETE On Session    ${API_ALIAS}    ${endpoint}/${resource_id}    expected_status=any
    Should Be Equal As Integers    ${response.status_code}    409

Assert Integer Difference
    [Arguments]    ${before}    ${after}    ${delta}
    ${expected}=    Evaluate    int(${before}) - int(${delta})
    Should Be Equal As Integers    ${after}    ${expected}

Assert Equal Integer Fields
    [Arguments]    ${body}    ${field_name}    ${expected_value}
    ${actual}=    Get From Dictionary    ${body}    ${field_name}
    Should Be Equal As Integers    ${actual}    ${expected_value}
