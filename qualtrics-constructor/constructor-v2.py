import json
import os
import copy

text_block = '{"SurveyID": "SV_difBGn1hgK9n2aq", "Element": "SQ", "PrimaryAttribute": "[INJECT_DIFF_Q_NUM]", "SecondaryAttribute": "inject summary 2", "TertiaryAttribute": null, "Payload": {"QuestionText": "[INSERT_TEXT]<br>", "DefaultChoices": false, "QuestionType": "DB", "Selector": "TB", "DataVisibility": {"Private": false, "Hidden": false}, "Configuration": {"QuestionDescriptionOption": "UseText"}, "QuestionDescription": "", "ChoiceOrder": [], "Validation": {"Settings": {"Type": "None"}}, "GradingData": [], "Language": [], "NextChoiceId": 4, "NextAnswerId": 1, "QuestionText_Unsafe": "inject summary 2<br>", "DataExportTag": "[INJECT_DIFF_Q_NUM]", "QuestionID": "[INJECT_DIFF_Q_NUM]"}}'
sample_block = '{"SurveyID":"SV_difBGn1hgK9n2aq","Element":"SQ","PrimaryAttribute":"[INJECT_DIFF_Q_NUM]","SecondaryAttribute":"Now, please write down as many activities as possible that happen today (Day 2) below according to the given summaries.","TertiaryAttribute":null,"Payload":{"QuestionText":"Now, please write down as many activities as possible that happen today (Day 2) below according to the given summaries.<br>","DefaultChoices":false,"QuestionType":"SBS","Selector":"SBSMatrix","Configuration":{"QuestionDescriptionOption":"UseText","RepeatHeaders":"none"},"QuestionDescription":"Now, please write down as many activities as possible that happen today (Day 2) below according to the given summaries.","Choices":{"1":{"Display":"Activity 1"},"2":{"Display":"Activity 2"},"3":{"Display":"Activity 3"},"4":{"Display":"Activity 4"},"5":{"Display":"Activity 5"},"6":{"Display":"Activity 6"},"7":{"Display":"Activity 7"},"8":{"Display":"Activity 8"},"9":{"Display":"Activity 9"},"10":{"Display":"Activity 10"},"11":{"Display":"Activity 11"},"12":{"Display":"Activity 12"},"13":{"Display":"Activity 13"},"14":{"Display":"Activity 14"},"15":{"Display":"Activity 15"},"16":{"Display":"Activity 16"},"17":{"Display":"Activity 17"},"18":{"Display":"Activity 18"},"19":{"Display":"Activity 19"},"20":{"Display":"Activity 20"}},"ChoiceOrder":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],"Validation":{"Settings":{"ForceResponse":"OFF","Type":"None"}},"GradingData":[],"Language":[],"NextChoiceId":21,"NextAnswerId":2,"NumberOfQuestions":1,"AdditionalQuestions":{"1":{"Answers":{"1":{"Display":"Activity Name"},"2":{"Display":"Activity Start Time"}},"QuestionText":"Activities Today","RecodeValues":[],"VariableNaming":[],"AnalyzeChoices":[],"QuestionType":"Matrix","Selector":"TE","SubSelector":"Long","ChoiceColumnWidthPixels":null,"DataExportTag":"[INJECT_DIFF_Q_NUM]#1","QuestionID":"[INJECT_DIFF_Q_NUM]#1","Choices":{"1":{"Display":"Activity 1"},"2":{"Display":"Activity 2"},"3":{"Display":"Activity 3"},"4":{"Display":"Activity 4"},"5":{"Display":"Activity 5"},"6":{"Display":"Activity 6"},"7":{"Display":"Activity 7"},"8":{"Display":"Activity 8"},"9":{"Display":"Activity 9"},"10":{"Display":"Activity 10"},"11":{"Display":"Activity 11"},"12":{"Display":"Activity 12"},"13":{"Display":"Activity 13"},"14":{"Display":"Activity 14"},"15":{"Display":"Activity 15"},"16":{"Display":"Activity 16"},"17":{"Display":"Activity 17"},"18":{"Display":"Activity 18"},"19":{"Display":"Activity 19"},"20":{"Display":"Activity 20"}},"ChoiceDataExportTags":false,"QuestionDescription":"Activities Today","Configuration":{"QuestionDescriptionOption":"UseText"}}},"ChoiceDataExportTags":false,"DataVisibility":{"Private":false,"Hidden":false},"QuestionText_Unsafe":"Now, please write down as many activities as possible that happen today (Day 2) below according to the given summaries.<br>","DataExportTag":"[INJECT_DIFF_Q_NUM]","QuestionID":"[INJECT_DIFF_Q_NUM]"}}'

def inject_block(qualtric_obj, q_num, prior_sum, today_sum):

    base_num = (100 + q_num)

    question = json.loads(sample_block.replace("[INJECT_DIFF_Q_NUM]", f'QID{base_num}0'))
    sum1 = json.loads(text_block.replace("[INJECT_DIFF_Q_NUM]", f'QID{base_num}1').replace("[INSERT_TEXT]", "<b> Day 1: </b>" + prior_sum))
    sum2 = json.loads(text_block.replace("[INJECT_DIFF_Q_NUM]", f'QID{base_num}2').replace("[INSERT_TEXT]", "<b> Day 2: </b>" + today_sum + "<hr>"))
    outro = json.loads(text_block.replace("[INJECT_DIFF_Q_NUM]", f'QID{base_num}3').replace("[INSERT_TEXT]", "This is a summary for a different person. Please read the summaries carefully."))
    
    # # add the elements
    # qualtric_obj["SurveyElements"].append(question)
    # qualtric_obj["SurveyElements"].append(sum2)
    # qualtric_obj["SurveyElements"].append(sum1)
    # qualtric_obj["SurveyElements"].append(outro)

    # # create block
    # block_id = f"BL_{base_num}"
    # qualtric_obj["SurveyElements"][0]["Payload"][f"{base_num}"] = {
    #     "Type": "Standard",
    #     "SubType": "",
    #     "Description": "sample-example",
    #     "ID": block_id,
    #     "BlockElements": [
    #     {
    #         "Type": "Question",
    #         "QuestionID": f"QID{base_num}3"
    #     },
    #     {
    #         "Type": "Page Break"
    #     },
    #     {
    #         "Type": "Question",
    #         "QuestionID": f"QID{base_num}1"
    #     },
    #     {
    #         "Type": "Page Break"
    #     },
    #     {
    #         "Type": "Question",
    #         "QuestionID": f"QID{base_num}2"
    #     },
    #     {
    #         "Type": "Question",
    #         "QuestionID": f"QID{base_num}0"
    #     }
    #     ]
    # }
    # # add block 


    # # add to flow
    # qualtric_obj['SurveyElements'][1]["Payload"]["Flow"][1]['Flow'].append({
    #     'Type':'Standard',
    #     'ID': block_id,
    #     'FlowID': f'FL_{base_num}',
    #     'Autofill': []
    # })

    # update the count
    qualtric_obj['SurveyElements'][7]["SecondaryAttribute"] = str(4 + int(qualtric_obj['SurveyElements'][7]["SecondaryAttribute"]))
    
import random
import csv
def main():

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("base-v2.qsf", 'r') as f:
        qualtric_obj = json.load(f)

        qualtric_obj["SurveyEntry"]["SurveyName"] = "summary-control-v2"

        # clear out the exisiting surveys in the randomizer
        qualtric_obj['SurveyElements'][1]["Payload"]["Flow"][2]['Flow'] = []
        qualtric_obj['SurveyElements'][1]["Payload"]["Flow"][2]['SubSet'] = 1

        # find the block about the summary
        block_description = [p for i,p in qualtric_obj['SurveyElements'][0]["Payload"].items() if p['Description'] == 'sample-example']
        print(block_description)
        # random.seed(42)

        example_timing =  qualtric_obj['SurveyElements'][-1]
        example_split_label = qualtric_obj['SurveyElements'][-11]
        example_summary_box = qualtric_obj['SurveyElements'][-14] # "Summaries - S4E2"
        example_questions = qualtric_obj['SurveyElements'][-26]

        intro_to_duc =  [e for e in qualtric_obj['SurveyElements'] if e['PrimaryAttribute'] == 'QID2'][0]
        
        example_duc_1 = qualtric_obj['SurveyElements'][-35] # Non-redundancy
        example_duc_2 = qualtric_obj['SurveyElements'][-23] # Structure
        example_duc_3 = qualtric_obj['SurveyElements'][-24] # Referential
        example_duc_4 = qualtric_obj['SurveyElements'][-37] # Grammer
        example_duc_5 = qualtric_obj['SurveyElements'][-39] # Focus





        # with open('../datasets/schedule-prev-anomaly-v3/persona-all.test.csv', 'r') as csvfile:
        #     reader = csv.reader(csvfile, delimiter=',')
        #     # entries
        #     next(reader)
        #     entries = []
        #     for row in reader:
        #         if row[2] != "":
        #             entries.append((row[2], row[3]))
        
        # random.shuffle(entries)

        # for i in range(100):
        #     inject_block(qualtric_obj, i, entries[i][0], entries[i][1])
    
        # #inject_block(qualtric_obj, 0, 'This is a summary yesterday', 'this is a summary today')


        with open("base-v2-e.qsf", 'w') as f:
            json.dump(qualtric_obj, f, indent=4)




if __name__ == "__main__":
    main()