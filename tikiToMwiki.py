# -*- coding: utf-8 -*-
#       © Crown copyright 2008 - Rosie Clarkson, Chris Eveleigh (development@planningportal.gov.uk) for the Planning Portal
#
#       You may re-use the Crown copyright protected material (not including the Royal Arms and other departmental or agency logos)
#       free of charge in any format. The material must be acknowledged as Crown copyright and the source given.
#
#
# 23/03/2009 Patched by Miguel Tremblay, Environment Canada
#  Script is now supposed to be functionnal
#   with french characters in UTF-8
# 6 Dec 2012 fix from Andrew White at Typesafe
########################################################

import sys,os,time,tarfile
from email.Parser import Parser
from xml.dom import minidom
import xml.parsers.expat
import xml.sax.saxutils as saxutils
import htmlentitydefs
from HTMLParser import HTMLParser
from urllib import quote,unquote
from urlparse import urljoin
from optparse import OptionParser
import re # get regex for syntaxhighlighting

#add any other links you may want to map between wikis here
url_maps = {'http://tikiwiki.org/RFCWiki':'http://meta.wikimedia.org/wiki/Cheatsheet'}

# Lookup table for TikiWiki downloads
downloads = {13: ('Ablauf Fragebogenerstellung Limesurvey NICHT anonym.doc', 'LimeSurvey 1.53 Databaseoperations when creating a survey', 'files70026008da3f5de361217358fe269c59'),
80: ('replacements.xlsx', 'Expression Manager Roadmap', '7d90ce9fb6eef5f9331c12c499e7d2d3'),
11: ('Ablauf Fragebogenerstellung Limesurvey anonym.doc', 'LimeSurvey 1.53 Databaseoperations when creating a survey', 'files1f05a55d78f168d7f7b9555a00ce6fc4'),
12: ('Databaseoperations when creating a survey.pdf', 'LimeSurvey 1.53 Databaseoperations when creating a survey', 'files41994bc5d54be9b4f4e1563fa0a94ae8'),
81: ('On-page-report-generation.lsg', 'Expression Manager HowTos', 'b03db129dcec7c7bbb09d5fb27a8315e'),
3 : ('instructions.html', 'Documentazione Italiano', 'filesb0d9f170961f25a757413fe1eef2add2'),
19: ('umfrage_erstellen.swf', 'Deutsche Anleitung für LimeSurvey', '29df48eed93534e275b03cd5c865a901'),
51: ('Database_Layout_Limesurvey_1.8.xls', 'LimeSurvey 1.8 database layout documentation', '§fb5f235bf70e94f99b9e29d319711c21§'),
4 : ('instructions.html', '說明文件', 'filesb0d9f170961f25a757413fe1eef2add2'),
9 : ('Database Layout Limesurvey 1.53.xls', 'LimeSurvey 1.53 database layout documentation', 'filesc3e0bf9ac3d4831e7d0bebf82e971035'),
5 : ('Spanish Manual PHPSurveyor v.1.43rc.pdf', 'Manual de Instrucciones en Español', 'files0cfdaa64fecb61c32a4922af0428cfb9'),
47: ('resetadminpw.php', 'General FAQ', '§c22ee7d80475c3a70ce70f1b9ab67a6c§'),
82: ('tailoring2.lsg', 'Expression Manager HowTos', 'b608fde7af0ad9eac8d5baeefc732e2e'),
21: ('Limesurvey Auswertungsmöglichkeiten Übersicht.doc', 'Statistik', 'a32225ab49f78cc9c3bca96e91bb88aa'),
22: ('newAssignment.ep', 'Interaction Design Mockups', '4f4c3c3603df80e7de67d1827c87dd4d'),
23: ('assignmentWorkflow.ep', 'Interaction Design Mockups', '53ce2ef418e8abeb4a7e56dc13d525f0'),
24: ('adminsection.ep', 'Interaction Design Mockups', 'de689bb2621950a0712e5ce8586c5881'),
25: ('manual_improvement.doc', 'Manual guideline', '0b89af65a6c99eb9888e6344fe19bb75'),
27: ('database-operations-on-survey-creation.pdf', 'LimeSurvey 1.53 database operations on survey creation', '9a0bbc66a5173417a13c655585e4aff6'),
28: ('F - Array Flexible Labels.csv', 'Question types', 'a038704324900f2247d878755e4f1ab2'),
29: ('H - Array Flexible Labels by Column.csv', 'Question types', '33f9b8f870298e49699d8d4e67afe46c'),
30: ('H - Array Flexible Labels - Semantic Differential.csv', 'Question types', '4da5d1f704dcbf42195f04d083a5569c'),
31: ('1 - Dual Scale.csv', 'Question types', 'd0992941dfa6dded54530aadb863425b'),
32: ('1 - Dual Scale Drop Down.csv', 'Question types', 'a9289687821efd2c0a5881eee99af112'),
33: ('DP - Array Multi Flexi Numbers.csv', 'Question types', '8496be0b0800e1340b8b6cd93523fbc4'),
34: ('DP - Array Multi Flexi Numbers Checkbox.csv', 'Question types', 'bd28ce35ad7e383e75d5e827add12d09'),
35: ('DP - Array Multi Flexi Text.csv', 'Question types', 'd9c2b4c4854b553c0f2f4e8670e434ef'),
36: ('K - Multiple Numerical eq 10.csv', 'Question types', '854781abb6abebe00a1217fb789a3486'),
37: ('K - Multiple Numerical eq 10 Slider.csv', 'Question types', '1b10d372f5b2cfcc22859eb2f0435446'),
39: ('R - Ranking.csv', 'Question types', '7f27580e60209dbc13649a75f34b6c8a'),
40: ('P - Multiple Options with Comments.csv', 'Question types', 'ed65b14c9000533e97a4f436e1f140fa'),
41: ('W - List Flexible Labels Dropdown.csv', 'Question types', 'a1515a87f71a209770e22df309f0fb11'),
42: ('Z - List Flexible Labels Radio.csv', 'Question types', '5cb40c3a71471e289e6c3c5f3dd443c9'),
43: ('prefill_date.php', 'Workarounds', 'a4e499f0bf7381845bd9ed3774b21dc8'),
45: ('users.csv', 'LimeSurvey 2 development demo test ride', '§94c3f78b963dbe8caa6cb7e6e920006c§'),
46: ('fake_adresses.csv', 'Zugangsschlüssel', '§bd5a2bd6ef02245d88777df5b56b7ca2§'),
52: ('users.csv', 'LimeSurvey 2 development demo test ride', '§991c3e628adcb85db8186b8348bd99b1§'),
53: ('Question Attributes-Revised.lss', 'Advanced question settings', 'e162795ff01014f840b882fdea99c76e'),
54: ('Limesurvey_sample_survey__Array_Filter_and_Exclusion.lss', 'Advanced question settings', '0b7c458819f3bddea8fda38471016c70'),
55: ('Limesurvey_sample_survey__Question_Attributes.lss', 'Advanced question settings', 'de71cdb0a2546f2a0dbcbd5f4452ce18'),
56: ('Limesurvey_sample_survey__Conditions.lss', 'Setting conditions', 'f21f65060b67d19b610373ac84047aed'),
58: ('Limesurvey_sample_survey__Conditions.lss', 'Bedingungen setzen', '6813e7fb143fcac8b5c229af641e3b3c'),
60: ('Limesurvey_sample_survey__Assessment.lss', 'Bewertungsregeln', 'b1abd49bd0c9f28379d5973edc19a754'),
61: ('Limesurvey_sample_survey__Quotas.lss', 'Quotas', 'd2a52824f65057cb06b0691d8b80a5fe'),
62: ('Limesurvey_sample_survey__Quotas.lss', 'Umfrage-Quoten', '76405afadf2310fda9aa07bf47a5456b'),
63: ('1 - Dual Scale.csv', 'Question type - Array dual scale', '3b02533258f5b46afbacfd158bb16aba'),
64: ('1 - Dual Scale Drop Down.csv', 'Question type - Array dual scale', '3c879c6d92fb3ed84e7ce5723fc21fcd'),
65: ('DP - Array Multi Flexi Numbers.csv', 'Question type - Array Num: (ers)', '9fdc0d724469ab6a985585f31f369252'),
66: ('DP - Array Multi Flexi Numbers Checkbox.csv', 'Question type - Array Num: (ers)', 'cd57fa0f796557689f549e4b04b4c034'),
67: ('F - Array Flexible Labels.csv', 'Question type - Array', '2b72b766e637339f03cfce43716a4c4e'),
68: ('H - Array Flexible Labels - Semantic Differential.csv', 'Question type - Array', '932bbc4429bfb8f45b3d1cb50473b8c3'),
70: ('H - Array Flexible Labels by Column.csv', 'Question type - Array by column', '8acf916efe5a4f0f54a49a58e1207fba'),
71: ('K - Multiple Numerical eq 10 Slider.csv', 'Question type - Multiple numerical input', '2069abcd996d37e29dc1d040babed2c9'),
74: ('P - Multiple Options with Comments.csv', 'Question type - Multiple choice with comments', '7a2167732c615f190e2ead646d883a34'),
73: ('K - Multiple Numerical eq 10.csv', 'Question type - Multiple numerical input', 'd924fa870cac15efe45688dc45a41b64'),
75: ('R - Ranking.csv', 'Question type - Ranking', '9bb32e4c06bca5827c47936db8e42637'),
76: ('W - List Flexible Labels Dropdown.csv', 'Question type - List Dro: (down)', '37a6f3b70f85ed03d2c8e1dfa6ba067b'),
77: ('Z - List Flexible Labels Radio.csv', 'Question type - List Rad: (o)', '4de70c7985912a5b76ddd6a0d38e4491'),
78: ('print_30.png', 'Optional settings', '1acb8a12cb50f70b37161a1b06c5c8d7'),
79: ('printable_survey.png', 'Optional settings', '734b1adca4aa4bb131d02e4bb1187416'),
83: ('ajouter-invitation.png', 'Invitations', 'ff8efa2502c935caa8a3ec567f5b5dbb'),
84: ('bascule-acces-restreint.png', 'Invitations', 'ecb25963a226abc5acabaa904a04bbf6'),
85: ('creer-codes-factives.png', 'Invitations', 'c17a78b1e30ce7e3dd4c111925f80bf9'),
86: ('edition-invitation.png', 'Invitations', '81d2d092489ac8438b7a8b74364e7320'),
88: ('envoi-invitation.png', 'Invitations', '14d39438a316f7079096eae33d16e4bd'),
89: ('import-CSV-invitation.png', 'Invitations', 'bb4abfa1715b3c95e224e325bab48070'),
90: ('parametres-rejet.png', 'Invitations', '4e22e819eaa81110062f35f0444a5983'),
91: ('recap-invitations.png', 'Invitations', '6b62706284cdf44fcd6d8945f2f42759'),
92: ('envoi-rappel-invitation.png', 'Invitations', 'acdd794af6159d4436d74fab26a1f91d'),
93: ('limeEr.jpg', 'LimeSurvey 1.8 database layout documentation', '61ddcf4663d62d8a3cb4af7278620d1a'),
94: ('GCI LimeSurvey Google Analytics Report.pdf', 'LimeSurvey Google Code-in 2011', 'b71cdaa7e8d21cbc99837fc57dae2796'),
95: ('LimeSurvey Question Type Survey Summary-1.pdf', 'LimeSurvey Google Code-in 2011', '1220e2d90ce3c2e96d67d1003297265d'),
96: ('Limesurvey Array Filter Demo Survey.lss', 'LimeSurvey Google Code-in 2011', 'dfc64638da12ab267e9328d53d78a6b2'),
97: ('Limesurvey Assessment Demo Survey.lss', 'LimeSurvey Google Code-in 2011', '83a2ef3da5792f142c4083307382d27d'),
98: ('Limesurvey Conditions Demo Survey.lss', 'LimeSurvey Google Code-in 2011', 'bb4a6b9107970bd9473c921ca5556734'),
99: ('Limesurvey Question Attribute Demo Survey.lss', 'LimeSurvey Google Code-in 2011', '50167b589612dd0429eb574aa15c232d'),
100: ( 'Limesurvey Quota Demo Survey.lss', 'LimeSurvey Google Code-in 2011', '364b45723aa6dc6ef936b4b29317a18a'),
101: ( 'ls2_cascading_array_filter.lss', 'Advanced question settings', '0cba8c2501ad2c5414c0ab36108c1ad3'),
102: ( 'limesurvey_group_32.lsg', 'Advanced question settings', '371bd74af3714120e2cb8f5d46969f93'),
103: ( 'limesurvey_group_33.lsg', 'Expression Manager HowTos', '7c661b7505e43835166627f827c8c44d'),
104: ( 'limesurvey_survey_53654.lss', 'Expression Manager Examples', '6a20e9dd4216d5d6de840d1c63f5cf65'),
111: ( 'ls2_cascading_array_filter.lss', 'Expression Manager Sample Surveys', '0a4ff256ccb2c8e8fd6c089cabe6074a'),
110: ( 'ls2_group_relevance.lss', 'Expression Manager Sample Surveys', '1e72df1663d38723587ee59dfcf3d427'),
112: ( 'ls2_EM_question_attributes.lss', 'Expression Manager Sample Surveys', '72cdb5e32567e39f3d3adbefd367b6d4'),
133: ( 'limesurvey_survey_62584.lss', 'Workarounds: Question design, layout and templating', '7e4ec9d2492eaa6876462402935159c0'),
113: ( 'ls2_validation_tests.lss', 'Expression Manager Sample Surveys', '5f8ce71e67fcf115396fea3290fb54d1'),
114: ( 'ls2_test_em_sq_validation.lss', 'Expression Manager Sample Surveys', 'f0eaf142b5cedfe907a3c82eb0fff2b0'),
115: ( 'ls2_subquestion_relevance.lss', 'Expression Manager Sample Surveys', 'f6b1299063968e033f8c8c3436a65a77'),
116: ( 'ls2_comma_as_radix_separator.lss', 'Expression Manager Sample Surveys', 'aec488d6f081639d04bf7f961e1f4ad6'),
117: ( 'Randomization_Group_Test.lss', 'Expression Manager Sample Surveys', 'd9ca00e4ae273a3b2b5a6047a09f1498'),
118: ( 'ls2_em_tailoring.lss', 'Expression Manager Sample Surveys', 'f603e560a33a149838efa33d06db749e'),
119: ( 'ls2_em_tailoring.xls', 'Excel Survey Structure', 'f2e614cb67956f497dc1992ff492480f'),
120: ( 'ls2_group_relevance.xls', 'Excel Survey Structure', 'ce6bd903ccae21ddae1a88c019a19f11'),
121: ( 'ls2_cascading_array_filter.xls', 'Excel Survey Structure', 'f1f531146c888daefd1d504c2a164a9e'),
122: ( 'ls2_validation_tests.xls', 'Excel Survey Structure', '93d24f5739c653627183767c41e37ba5'),
123: ( 'Randomization_Group_Test.xls', 'Excel Survey Structure', '3b208c88c4a3449b90f624f144379d88'),
124: ( 'limesurvey_survey_55164.lss', 'Expression Manager Sample Surveys', '14b879ce95567a110e03ae547850ef25'),
125: ( 'limesurvey_survey_55164.lss', 'Expression Manager Sample Surveys', '6f0d3d605de0dce1b1af3c82c36e94d6'),
126: ( 'rating_user_entered_list_of_products.lss', 'Expression Manager Sample Surveys', 'ff9eeac11ee265ddd79ef3e500cac0fe'),
127: ( 'rating_user_entered_list_of_products.lss', 'Expression Manager Sample Surveys', 'd52fd2136508438e780605e177bcdeb0'),
128: ( 'semantic_differential.lsq', 'Fragetypen', '73f30bcc78650ae5e534be6dc4cd3b1b'),
132: ( 'imagetick_lime_v1.3.zip', 'Workarounds: Question design, layout and templating', '39ea3d67cc18ba9606894c376957bfb1'),
134: ( 'default_vertical_sliders.zip', 'Workarounds: Question design, layout and templating', 'fb566be7b63be3e39a862922db5a47b2'),
136: ( 'imagetick_lime_v2.zip', 'Workarounds: Question design, layout and templating', 'e76283e9e545e43bb142b0d995e0f9f9'),
139: ( 'demo_vertical_sliders.lss', 'Workarounds: Question design, layout and templating', '84f1ba8e126943a335cc30e654c1fe8f')}

#checks for HTML tags
class HTMLChecker(HTMLParser):

        def handle_starttag(self, tag, attrs):
                global validate
                validate = True
                return True
        def handle_endtag(self, tag):
                global validate
                return True

#Mediawiki relies on having the right number of new lines between syntax - for example having two new lines in a list starts a new list.
#The elements that do/don't start a new line in HTML can be controlled by the CSS. The CSS used depends on which skin you're using.
class HTMLToMwiki(HTMLParser):
        global wikitext
        global sourceurl
        global pages
        global uploads
        global headings
        link = False #if the parser is within a link
        src = ''
        innowiki = False
        inem = False #if the parser is within italics
        instrong = False #if the parser is within bold
        inheading = False #if the parser is within a heading
        list=0 #whether the parser is within an ordered list (is numeric to deal with nested lists)
        litem=0 #whether the parser is within a list item - in order to deal with <p> and <br/> tags in ways that wont break it
        ul_count=0 #the number of ul tags used for nested lists
        ol_count=0 #the number of ol tags used for nested lists
        col_count=0
        def handle_starttag(self, tag, attrs):
                if self.innowiki:
                        completeTag='<'+tag
                        for attr in attrs:
                                completeTag+=' '+attr[0]+'="'+attr[1]+'"'
                        wikitext.append(completeTag+'>')
                else:
                        if tag == 'nowiki':
                                wikitext.append('<nowiki>')
                                self.innowiki=True
                        if tag == 'a':
                                self.src=''
                                for att in attrs:
                                        if att[0] == 'href':
                                                self.src = att[1]
                                if self.src in url_maps:
                                        self.src=url_maps[self.src]
                                #deals with uploads
                                if 'tiki-download_file.php' in self.src:
                                        uploads.append(self.src)
                                if 'tiki-download_wiki_attachment.php' in self.src:
                                        uploads.append(self.src)
                                self.link=True
                        if tag == 'ol':
                                self.ol_count+=1
                                self.list+=1

                        if tag == 'ul':
                                self.ul_count+=1
                        if tag == 'li':
                                #append the right no. of # or *s according to the level of nesting
                                self.litem+=1
                                if self.list>0:
                                        wikitext.append('\n'+('#'*self.ol_count))
                                else:
                                        wikitext.append('\n'+('*'*self.ul_count))
                        if tag == 'img':
                                src=''
                                for att in attrs:
                                        if att[0] == 'src':
                                                src = att[1]
                                src = quote(src)
                                #we have several different ways of specifying image sources in our tiki
                                imagepath = urljoin(sourceurl, src)
                                if options.newImagepath != '':
                                        imagepath=urljoin(options.newImagepath, src.split('/')[-1])
                                # the pic tag is used later to identify this as a picture and process the correct mwiki syntax
                                wikitext.append('<pic>'+imagepath+' ')
                        if tag == 'table':
                                wikitext.append('\n{|')
                                for att in attrs:
                                        #table formatting
                                        wikitext.append(' '+att[0]+'="'+att[1]+'"')
                        if tag == 'tr':
                                wikitext.append('\n|-')
                                self.col_count=0
                        if tag == 'td':
                                self.col_count+=1
                                if self.col_count > 1:
                                        wikitext.append('\n||')
                                else:
                                        wikitext.append('\n|')
                        if tag == 'caption':
                                wikitext.append('\n|+')
                        if tag in ('strong','b'):
                                self.instrong=True
                                wikitext.append("'''")
                        if tag in('em','i'):
                                self.inem=True
                                wikitext.append("''")
                        if tag =='p':
                                #new lines in the middle of lists break the list so we have to use the break tag
                                if self.litem==0:
                                        br = '\n'
                                else:
                                        br = '<br/>'
                                #newlines in the middle of formatted text break the formatting so we have to end and restart the formatting around the new lines
                                if self.inem==True:
                                        br = "''"+br+br+"''"
                                if self.instrong==True:
                                        br = "'''"+br+br+"'''"
                                wikitext.append(br)
                        if tag =='h1':
                                self.inheading = True
                                #headings must start on a new line
                                wikitext.append('\n\n==')
                                headings.append(tag)
                        if tag =='h2':
                                self.inheading = True
                                wikitext.append('\n\n===')
                                headings.append(tag)
                        if tag =='h3':
                                self.inheading = True
                                wikitext.append('\n\n====')
                                headings.append(tag)
                        else:
                                wikitext.append('<'+tag+'>')

        def handle_endtag(self, tag):
                if tag =='nowiki':
                        wikitext.append('</nowiki>')
                        self.innowiki=False
                if not self.innowiki:
                        if self.link==True:
                                self.src=''
                                self.link=False
                        if tag == 'img':
                                wikitext.append('</pic>')
                        if tag == 'ol':
                                self.ol_count-=1
                                self.list-=1
                                wikitext.append('\n\n')
                        if tag == 'ul':
                                self.ul_count-=1
                                wikitext.append('\n\n')
                        if tag == 'li':
                                self.litem-=1
                        if tag == 'table':
                                wikitext.append('\n\n|}')
                        if tag in('strong','b'):
                                self.instrong=False
                                wikitext.append("'''")
                        if tag in('em','i'):
                                self.inem=False
                                wikitext.append("''")
                        if tag =='h1':
                                self.inheading = False
                                wikitext.append('==\n\n')
                        if tag =='h2':
                                self.inheading = False
                                wikitext.append('===\n\n')
                        if tag =='h3':
                                self.inheading = False
                                wikitext.append('====\n\n')
                        if tag =='p':
                                if self.inheading == True:
                                        br=''
                                elif self.litem==0:
                                        br = '\n'
                                else:
                                        br = '<br/>'
                                if self.inem==True:
                                        br = " ''"+br+"''"
                                if self.instrong==True:
                                        br = " '''"+br+"'''"
                                wikitext.append(br)
                        if tag == 'br':
                                if self.inheading == True:
                                        br=''
                                elif self.litem==0:
                                        br = '\n'
                                else:
                                        br = '<br/>'
                                if self.inem==True:
                                        br = " ''"+br+"''"
                                if self.instrong==True:
                                        br = " '''"+br+"'''"
                                wikitext.append(br)
                        if tag == 'hr':
                                wikitext.append('\n----\n')
                        else:
                                wikitext.append('</'+tag+'>')
                else:
                        wikitext.append('</'+tag+'>')
        #check for symbols which are mwiki syntax when at the start of a line
        def check_append(self,data):
                stripped = data.lstrip()
                for symbol in ('----','*','#','{|','==','===','===='):
                        if stripped.startswith(symbol):
                                if len(wikitext) > 2 and wikitext[-3] == '\n':
                                        if not symbol.startswith('='):
                                                data= '<nowiki>'+symbol+'</nowiki>'+stripped[len(symbol):]
                                        else:
                                                if data.find(symbol,len(symbol)):
                                                        data= '<nowiki>'+symbol+'</nowiki>'+stripped[len(symbol):]
                return data

        def handle_data(self,data):
                if self.link==True:
                        #sometimes spaces are in the piped data (probably because of our editor) so we need to make sure we add that before the link
                        space = ''
                        if data.startswith(' '):
                                space = ' '
                        if self.src.startswith(sourceurl+'tiki-download_wiki_attachment.php'):
                                wikitext.append(space+'['+self.src+' '+data+']')
                        elif self.src.startswith(sourceurl):
                                if 'page=' in self.src:
                                        ptitle = self.src.split('page=')
                                        page = ptitle[1].replace('+',' ')
                                        for file in pages:
                                                #mwiki is case sensitive to page names and tikiwiki isn't so check that the file actually exists
                                                if file.lower()==page.lower():
                                                        page = file
                                        wikitext.append(space+'[['+page+'|'+data+']]')
                        else:
                                #catch relative urls
                                if self.src.startswith('..'):
                                        self.src = urljoin(sourceurl, self.src)
                                wikitext.append(space+'['+self.src+' '+data+']')
                elif self.litem:
                        # if we're in a list put nowiki tags around data begining with * or # so it isnt counted as nesting
                        if data[0] in ('*', '#'):
                                data = '<nowiki>'+data[0]+'</nowiki>'+data[1:]
                        wikitext.append(data)
                else:
                        data = self.check_append(data)
                        wikitext.append(data)

        def handle_entityref(self,data):
                data="&amp;"+data+";"
                if self.link:
                        wikitext.append(' '+data)
                elif self.litem:
                        wikitext.append(data)
                else:
                        wikitext.append(data)

        def handle_charref(self,data):
                data="&amp;"+data+";"
                if self.link:
                        wikitext.append(' '+data)
                elif self.litem:
                        wikitext.append(data)
                else:
                        wikitext.append(data)

def insertImage(word,words):
        global image
        global imagenames
        global imageids
        global imagepath
        global line
        #there are even more ways to specify pic sources in our tiki
        if 'src=' in line:
                if 'http' in line:
                        # print "external"
                        # print line.encode('utf-8')
                        lineparts = line.split('}')
                        parts = lineparts[0].split('=')
                        # print parts
                        try:
                                filename = parts[1][1:parts[1].find('"',1)]
                        except:
                                pass
                        imgfile = "%s%s" % (filename, '}'.join(lineparts[1:]))
                        # print imgfile.encode('utf-8')
                        line = imgfile
                        words.append(imgfile)
                else:
                        # print line.encode('utf-8')
                        lineparts = line.split('}')
                        parts = lineparts[0].split('=')
                        # print parts
                        try:
                                filename = parts[1][1:parts[1].find('"',1)]
                        except:
                                pass
                        filename = filename.replace('[', '_')
                        filename = filename.replace(']', '')
                        filename = filename.replace(imageurl, '')
                        imgfile = "[[File:%s]]%s" % (filename, '}'.join(lineparts[1:]))
                        # imgfile = "[[File:%s]]" % (filename)
                        # print imgfile.encode('utf-8')
                        line = imgfile
                        words.append(imgfile)
        # if 'name=' in word:
        #         parts = word.split('=')
        #         try:
        #                 filename = imagenames[parts[2]]
        #         except KeyError:
        #                 sys.stderr.write(parts[2]+' doesn\'t exist in your image XML file and won\'t be displayed properly\n')
        #                 filename=parts[2]
        #         filename = quote(filename)
        #         imagepath = urljoin(urljoin(sourceurl,imageurl), filename)
        #         if options.newImagepath != '':
        #                 imagepath=urljoin(options.newImagepath, filename)
        #         words.append('<pic>'+imagepath)
        # if 'id=' in word:
        #         parts = word.split('=')
        #         try:
        #                 filename = imageids[parts[2]]
        #         except KeyError:
        #                 sys.stderr.write( 'The image with ID '+parts[2]+' doesn\'t exist in your image XML file and won\'t be displayed properly\n')
        #                 filename=parts[2]
        #         filename = quote(filename)
        #         imagepath = urljoin(urljoin(sourceurl,imageurl), filename)
        #         if options.newImagepath != '':
        #                 imagepath=urljoin(options.newImagepath, filename)
        #         words.append('<pic>'+imagepath)
        if '}' in word:
                bracket=word.find('}')
                if word[-1]!='}':
                        if word[bracket+1]!=' ':
                                word=word.replace('}','</pic> ')
                        else:
                                word=word.replace('}','</pic>')
                word=word.replace('}','</pic>')
                words.append(word)
                image = False

        return words

def insertLink(word):
        global intLink
        global page
        global words
        global pages
        first=False
        #the link may be split if it contains spaces so it may be sent in parts
        brackets=word.find('((')
        if brackets != -1:
                word = word.replace('((','[[')
                page = word[brackets:]
                words.append(word[:brackets])
                if '))' in word:
                        word = word.replace('))',']]')
                        end=word.find(']]')
                        text = word[brackets+2:end]
                        #again check the filenames to ensure case sensitivity is ok
                        for file in pages:
                                if unicode(file, "Latin-1").lower() \
                                        == text.lower():
                                        text = file
                        text = '[['+text+word[end:]
                        if text[-1]!='\n':
                                words.append(text+' ')
                        else:
                                words.append(text)
                        page = ''
                        intLink=False

        elif '))' in word:
                word = word.replace('))',']]')
                page += ' '+word
                pipe = page.find('|')
                if pipe != -1:
                        end=pipe
                        text= page[2:pipe]
                else:
                        brackets=page.find(']]')
                        end=brackets
                        text= page[2:brackets]
                for file in pages:
                        if unicode(file, "latin-1").lower()==text.lower():
                                page=page[:2]+file+page[end:]
                if page[-1]!='\n':
                        words.append(page+' ')
                else:
                        words.append(page)
                page = ''
                intLink=False
        else:
                first=False
                page += ' '+word

parser = OptionParser()
parser.add_option("-n", "--notableofcontents",
                  action="store_true", dest="notoc", default=False,
                  help="disable all automatic contents tables")
parser.add_option("-m", "--maxfilesize",
                  action="store", type="int", dest="max", default=1,
                  help="the maximum import file size")
parser.add_option("-j", "--newimageurl",
                  action="store", type="string", dest="newImagepath", default='',
                  help="the new location of any images (inc. trailing slash)")
parser.add_option("-i", "--imageurl",
                  action="store", type="string", dest="imageurl", default='',
                  help="the relative URL used in tiki to access images (inc. trailing slash)")
parser.add_option("-p", "--privatepages",
                  action="store", type="string", dest="privatexml", default='',
                  help="an XML file containing any private pages not to be added to the wiki")
parser.add_option("-o", "--outputfile",
                  action="store", type="string", dest="outputFile", default='',
                  help="the name of the output wiki XML file(s)")
parser.add_option("-k", "--imagexml",
                  action="store", type="string", dest="imagexml", default='',
                  help="an XML file containing metadata for the images in the tiki")

(options, args) = parser.parse_args()

# the tar file containing the tiki file export - if not specified read from stdin
#stdin doesn't work at the moment and fails after you've used extractfile as this returns nothing
if len(args)>1:
        archive = tarfile.open(args[1])
        #add all files in the export tar to the list of pages
        pages = archive.getnames()
        if options.outputFile=='':
                outputFile= args[1].replace('.tar','.xml')
        else:
                outputFile=options.outputFile
else:
        pages=[]
        #if reading from stdin you can't iterate through the files again so pages is left empty and links are not corrected
        archive = tarfile.open(name= sys.stdin.name, mode='r|', fileobj=sys.stdin)
        #if you're reading from stdin and don't specify an output file output to stdout
        if options.outputFile=='':
                options.outputFile='-'
p = Parser()

#multiple files may be created so this is added to the output file string to identify them
fileCount=0

#the string to name all outputfiles the fileCount is added to this
if options.outputFile=='-':
        mwikixml=sys.stdout
else:
        mwikixml = open(outputFile[:-4]+str(fileCount)+outputFile[-4:], 'wb')
        sys.stderr.write('Creating new wiki xml file '+outputFile[:-4]+str(fileCount)+outputFile[-4:])

#the source URL of the tiki - in the form http://[your url]/tiki/
sourceurl = args[0]

#the relative address used to access pictures in TikiWiki
imageurl = options.imageurl

privatePages=[]
if options.privatexml !='':
        privateparse =  minidom.parse(options.privatexml)
        rows=privateparse.getElementsByTagName('row')
        for row in rows:
                fields = row.getElementsByTagName('field')
                for field in fields:
                        if field.getAttribute('name')=='pageName':
                                privatePages.append(field.firstChild.data)
#fill the lookup table with the image information
#a file containing an xml dump from the tiki DB
imagenames={}
imageids={}
if options.imagexml !='':
        imagexml = options.imagexml
        lookup = minidom.parse(imagexml)

        rows = lookup.getElementsByTagName('row')
        for row in rows:
                fields = row.getElementsByTagName('field')
                for field in fields:
                        if field.getAttribute('name')=='name':
                                iname = field
                        if field.getAttribute('name')=='filename':
                                ifile = field
                        if field.getAttribute('name')=='imageID':
                                iid = field
                imagenames[iname.firstChild.data] = ifile.firstChild.data
                imageids[iid.firstChild.data] = ifile.firstChild.data



#list of users who have edited pages
authors = []
filepages = {}
totalSize=0
pagecount = 0
versioncount = 0

#write mediawiki xml file
mwikixml.write('<mediawiki xml:lang="en">\n')

for member in archive:
        if member.name not in privatePages:
                #add each file in the tiki export directory
                tikifile = archive.extractfile(member)
                mimefile = p.parse(tikifile)
                mwikixml.write('<page>\n')
                partcount=0
                uploads = []

                if not mimefile.is_multipart():
                        partcount =1
                for part in mimefile.walk():
                        outputpage=''
                        if partcount == 1:
                                title = unquote(part.get_param('pagename'))
                                outputpage += '<title>'+title+'</title>'
                        partcount+=1
                        if part.get_params() is not None and \
                                ('application/x-tikiwiki','') in part.get_params():
                                versioncount +=1
                                headings =[]
                                if part.get_param('lastmodified') == None:
                                        break
                                outputpage += '<revision>\n'
                                outputpage += '<timestamp>'+ \
                                     time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(eval(part.get_param('lastmodified'))))+'</timestamp>\n'
                                outputpage += '<contributor><username>'+part.get_param('author')+'</username></contributor>\n'
                                # add author to list of contributors to be output at the end
                                if part.get_param('author')not in authors:
                                        authors.append(part.get_param('author'))
                                outputpage += '<text xml:space="preserve">\n'
                                mwiki = ''
                                #we add the tiki description to the page in bold and italic (much as it was in tikiwiki)
                                #for them to function properly we need to ensure that these strings are followed by a new line
                                # the </br> is used as a placeholder and is converted to \n later
                                if part.get_param('description') not in(None,''):
                                        mwiki+="'''''"+unquote(part.get_param('description'))+"'''''</br>"
                                #then add the table of contents (or specify none)
                                if options.notoc: mwiki=mwiki + "__NOTOC__</br>"
                                else: mwiki+="__TOC__</br>"
                                mwiki += part.get_payload().decode('utf-8')


                                #does the validator do anything?!
                                validate = False
                                validator = HTMLChecker()
                                validator.feed(mwiki)
                                #fixes pages that end up on a single line (these were probably created by our WYSWYG editor being used on windows and linux)
                                if not validate:
                                        mwiki=mwiki.replace('\t', '    ')
                                        mwiki=mwiki.replace('  ', ' &nbsp;')
                                        mwiki=mwiki.replace('<', '&lt;')
                                        mwiki=mwiki.replace('>', '&gt;')

                                        #make sure newlines after headings are preserved
                                        next = 0
                                        while '\r\n!' in mwiki[next:] or '&lt;/br&gt;!' in mwiki[next:] or mwiki[next:].startswith('!'):
                                                if mwiki[next:].startswith('!'): found= next
                                                else:
                                                        foundreturn = mwiki.find('\r\n!', next)
                                                        foundbreak = mwiki.find('&lt;/br&gt;!', next)
                                                        if (foundreturn != -1 and foundreturn<foundbreak) or foundbreak==-1:
                                                                found = foundreturn+2
                                                        else:
                                                                found = foundbreak+11

                                                next = mwiki.find('\r\n', found)
                                                if next == -1: break
                                                mwiki=mwiki[:next]+'</br>'+mwiki[next+2:]
                                                next += 5

                                        #as validate is false the page does not contain any html so whitespace needs to be preserved
                                        mwiki=mwiki.replace('\r\n', '</br>')

                                #double escape < and > entities so that &lt; is not unescaped to < which is then treated as HTML tags
                                #mwiki=mwiki.replace('&amp;', '&amp;amp;')
                                mwiki=mwiki.replace('&amp;lt;', '&amp;amp;lt;')
                                mwiki=mwiki.replace('&amp;gt;', '&amp;amp;gt;')
                                mwiki=mwiki.replace('&lt;', '&amp;lt;')
                                mwiki=mwiki.replace('&gt;', '&amp;gt;')
                                mwiki=mwiki.replace(u'\ufffd', '&nbsp;')

                                # unescape XML entities
                                entitydefs = dict( ("&"+k+";", unichr(v)) for k, v in htmlentitydefs.name2codepoint.items() )
                                entitydefs.pop("&amp;")
                                entitydefs.pop("&gt;")
                                entitydefs.pop("&lt;")
                                mwiki=saxutils.unescape(mwiki, entitydefs)

                                # replace tiki syntax that will be interpreted badly with tiki syntax the parser will understand
                                #empty formatting tags will be converted to many "'"s which then confuses mwiki
                                mwiki = mwiki.replace('[[','~np~[~/np~')
                                #need to replace no wiki tags here in case any html/xml is inside them that we want to keep
                                mwiki=mwiki.replace('~np~', '<nowiki>')
                                mwiki=mwiki.replace('~/np~', '</nowiki>')
                                mwiki=mwiki.replace('<em></em>', '')
                                mwiki=mwiki.replace('<em><em>', '<em>')
                                mwiki=mwiki.replace('</em></em>', '</em>')
                                mwiki=mwiki.replace('<strong></strong>', '')
                                mwiki=mwiki.replace('<strong><strong>', '<strong>')
                                mwiki=mwiki.replace('</strong></strong>', '</strong>')
                                #this makes sure definitions keep their preceding newline
                                mwiki=mwiki.replace('\n;', '</br>;')
                                mwiki=mwiki.replace('\n', ' ')
                                mwiki=mwiki.replace('</br>', '\n')
                                mwiki=mwiki.replace('&lt;/br&gt;', '\n')
                                mwiki=mwiki.replace('\r', ' ')
                                mwiki=mwiki.replace('\t', ' ')

                                # Add nowiki tags around code snippets to preserve
                                mwiki=mwiki.replace('{CODE', '<nowiki>{CODE')
                                mwiki=mwiki.replace('{CODE}', '{CODE}</nowiki>')

                                # Remove extra {IMG} tags
                                mwiki = mwiki.replace('{IMG}', '')

                                # convert === underline syntax before the html converter as
                                # headings in mwiki use =s and h3 tags will become ===heading===
                                next = 0
                                while '===' in mwiki[next:]:
                                        start = mwiki.find('===', next)
                                        end = mwiki.find('===', start+3)

                                        if end != -1:
                                                mwiki = mwiki[:start]+'<u>'+mwiki[start+3:end]+'</u>'+mwiki[end+3:]
                                        next = start +1
                                        #if there is another === convert them both

                                #print mwiki


                                wikitext=[]

                                #convert any HTML tags to mediawiki syntax
                                htmlConverter = HTMLToMwiki()
                                htmlConverter.feed(mwiki)

                                mwiki = ''.join(wikitext)

                                #replace tiki syntax with mwiki
                                mwiki=mwiki.replace('__',"'''")

                                #split the text into lines and then strings to parse
                                words=[]
                                image=False
                                intLink=False
                                box=False
                                colour = False
                                inColourTag=False
                                page = ''
                                centre=False
                                inTable=False
                                for line in mwiki.splitlines(True):
                                        heading = False
                                        noCentre = False

                                        # Check for tables and format appropriately
                                        if line.strip()[:2] == '||':
                                                inTable = True
                                                line = line.strip()[2:]
                                                line = '{|\n|' + line.replace('|', '||') + '\n|-\n'
                                                # print "Table start Line %i" % count
                                                # print line,
                                        elif line.strip()[-2:] == '||':
                                                line = line.strip()[:-2]
                                                line = line.replace('|', '||')
                                                line = '|' + line + '\n|}\n'
                                                # print line,
                                                # print "Table END! Line %i" % count
                                                inTable = False
                                        elif inTable:
                                                line=line.replace('|', '||')
                                                line='|'+line+'|-\n'
                                                # print line,

                                        if '{file' in line:
                                                if 'name=' in line:
                                                        namestart = line.lower().index('{file')
                                                        before_text = line[:namestart]
                                                        src = line[namestart:line.index('}')+1]
                                                        after_text = line[line.index('}')+1:]
                                                        parts = src.split('=')
                                                        # print parts
                                                        filename = parts[1][1:parts[1].find('"',1)]
                                                        filename = filename.replace("'''", "__")
                                                        filename = filename.replace("__", "_")
                                                        filename = filename.replace(" ", "_")
                                                        desc = ''
                                                        if 'desc=' in line:
                                                                for part in parts:
                                                                        if 'desc' in part:
                                                                                desc = parts[parts.index(part)+1]
                                                                                desc = desc[1:desc.find('"',1)]
                                                        if desc != '':
                                                                filelink = "%s[[Media:%s|%s]]%s" % (before_text, filename, desc, after_text)
                                                        else:
                                                                filelink = "%s[[Media:%s|%s]]%s" % (before_text, filename, filename, after_text)
                                                        line = filelink
                                                        # print filelink.encode('utf-8')
                                        # handle images before splitting into words
                                        if '{img' in line or '{IMG' in line:
                                                if 'src=' in line:
                                                        imgstart = line.lower().index('{img')
                                                        before_text = line[:imgstart]
                                                        src = line[imgstart:line.index('}')+1]
                                                        after_text = line[line.index('}')+1:]
                                                        if 'http' in src:
                                                                parts = src.split('=')
                                                                # print parts
                                                                filename = parts[1][1:parts[1].find('"',1)]
                                                                imgfile = "%s%s%s" % (before_text, filename, after_text)
                                                                line = imgfile
                                                                # print imgfile.encode('utf-8')
                                                        else:
                                                                parts = src.split('=')
                                                                # print parts
                                                                try:
                                                                      filename = parts[1][1:parts[1].find('"',1)]
                                                                except:
                                                                      filename = ''
                                                                filename = filename.replace('[', '_')
                                                                filename = filename.replace(']', '')
                                                                filename = filename.replace(imageurl, '')
                                                                if filename == '':
                                                                        imgfile = "%s%s" % (before_text, after_text)
                                                                else:
                                                                        imgfile = "%s[[File:%s]]%s" % (before_text, filename, after_text)
                                                                line = imgfile
                                                                # print imgfile.encode('utf-8')

                                        #if there are an odd no. of ::s don't convert to centered text
                                        if line.count('::') % 2 != 0:
                                                noCentre =True
                                        count =0
                                        spl = line.split(' ')
                                        if spl[0].find('!') == 0: heading = True
                                        for word in spl:
                                                #handle headings
                                                if heading is True:
                                                        if count is 0 and word:
                                                                #replace !s
                                                                bangs =0;
                                                                while word[bangs]== '!':
                                                                        word=word.replace('!','=',1)
                                                                        bangs+=1
                                                                        if bangs >= len(word):
                                                                                if len(spl) == 1: bangs /= 2
                                                                                break
                                                        if count is len(spl)-1:
                                                                #add =s to end
                                                                end = word.find('\n')
                                                                if end != -1:
                                                                        word=word[:end]+(bangs*'=')+word[end:]
                                                                else:
                                                                        word=word[:end]+(bangs*'=')
                                                #handle centered text
                                                if '::' in word and not noCentre:
                                                        next=0
                                                        while '::' in word[next:]:
                                                                next = word.find('::')
                                                                if centre:
                                                                        centre = False
                                                                        word = word.replace('::','</center>',1)
                                                                else:
                                                                        centre = True
                                                                        word = word.replace('::','<center>',1)
                                                #handle font colours
                                                if inColourTag:
                                                        colon = word.find(':')
                                                        if colon != -1:
                                                                word = word[:colon]+'">'+word[colon+1:]
                                                                inColourTag=False
                                                if '~~' in word:
                                                        next=0
                                                        while '~~' in word[next:]:
                                                                next = word.find('~~')
                                                                if colour == True:
                                                                        #end span
                                                                        colour = False
                                                                        word = word.replace('~~','</span>',1)
                                                                else:
                                                                        #start span
                                                                        colour=True
                                                                        colon = word.find(':',next)
                                                                        extratext =''
                                                                        if colon != -1:
                                                                                word = word[:next]+"<span style='color:"+word[next+2:colon]+"'>"+word[colon+1:]
                                                                        else:
                                                                                word = word[:next]+'<span style="color:'+word[next+2:]
                                                                                inColourTag=True
                                                                next += 1
                                                # handle boxes
                                                if '^' in word:
                                                        hats = word.count('^')
                                                        for hat in range(1, hats+1):
                                                                index = word.find('^')
                                                                if not box:
                                                                        word = word[:index]+'<div class="simplebox">'+word[index+1:]
                                                                        box=True
                                                                else:
                                                                        word = word[:index]+'</div>'+word[index+1:]
                                                                        box=False
                                                if '{img' in word or '{IMG' in word:
                                                        # image = True
                                                        image = False
                                                if '((' in word:
                                                        intLink = True
                                                if image:
                                                        words = insertImage(word,words)
                                                elif intLink:
                                                        insertLink(word)
                                                else:
                                                        #stops mwiki automatically creating links (which can then be broken by formatting
                                                        if ('http' in word or 'ftp://' in word) and '[' not in word and ']' not in word and '<pic>' not in word and '<pre>' not in word and '</pre>' not in word and not box:
                                                                index = 0
                                                                format = False
                                                                formatted = ''
                                                                for char in word:
                                                                        index+=1
                                                                        if char == "'":
                                                                                if not format:
                                                                                        format= True
                                                                                        formatted = formatted+'</nowiki>'
                                                                        else:
                                                                                if format:
                                                                                        format = False
                                                                                        formatted = formatted+'<nowiki>'

                                                                        formatted +=char

                                                                # word = '<nowiki>'+formatted+'</nowiki>'
                                                        # Find and replace links with titles to display correctly
                                                        if '[http' in word or '[ftp://' in word:
                                                                if 'tiki-download_wiki_attachment.php' in word:
                                                                        uploads.append(word)
                                                                else:
                                                                        # Change links to MediaWiki Format
                                                                        index = word.find('|')
                                                                        if index != -1:
                                                                                word = word.replace('|', ' ')

                                                        if word != '':
                                                                if '\n' in word[-1]:
                                                                        words.append(word)
                                                                else:
                                                                        words.append(word+' ')
                                                count+=1

                                mwiki = ''.join(words)
                                #get rid of pic placeholder tags
                                mwiki=mwiki.replace("<pic>", "")
                                mwiki=mwiki.replace("</pic>", "")

                                #make sure there are no single newlines - mediawiki just ignores them. Replace multiple lines with single and then single with double.
                                while "\n\n" in mwiki or "\n \n" in mwiki:
                                        mwiki=mwiki.replace("\n\n", "\n")
                                        mwiki=mwiki.replace("\n \n", "\n")
                                mwiki=mwiki.replace('\n', '\n\n')

                                #replace multiple lines with single where they would break formatting - such as in a list
                                mwiki=mwiki.replace('\n\n#', '\n#')
                                mwiki=mwiki.replace('\n\n*', '\n*')
                                mwiki=mwiki.replace('*<br/>', '*')
                                mwiki=mwiki.replace('#<br/>', '#')
                                mwiki = mwiki.lstrip('\n')

                                lines=[]
                                for line in mwiki.splitlines(True):
                                        if line.startswith(':'):
                                                line='<nowiki>:</nowiki>'+line[1:]
                                        lines.append(line)
                                mwiki=''.join(lines)

                                # Replace syntax highlighting
                                mwiki=mwiki.replace('<nowiki><nowiki>', '<nowiki>')    # remove extra nowikis added somewhere
                                mwiki=mwiki.replace('</nowiki></nowiki>', '</nowiki>') # remove extra nowikis added somewhere
                                mwiki=mwiki.replace('<nowiki>{CODE}</nowiki>', '</syntaxhighlight>')
                                mwiki=re.sub('<nowiki>{CODE\(.*?colors\=\"([\w]+)\".*?\)}', '<syntaxhighlight lang=&quot;\\1&quot;>', mwiki)
                                mwiki=re.sub('<nowiki>{CODE\(.*?\)}', '<syntaxhighlight lang=&quot;php&quot;>', mwiki)


                                entitydefs = dict( (unichr(k), "&amp;"+v+";") for k, v in htmlentitydefs.codepoint2name.items() )
                                entitydefs.pop('<')
                                entitydefs.pop('>')
                                entitydefs.pop('&')
                                mwiki=saxutils.escape(mwiki, entitydefs)

                                for n in range(len(mwiki)):
                                        if mwiki[n]< " " and mwiki[n]!='\n' and mwiki[n]!='\r' and mwiki[n]!='\t':
                                                mwiki=mwiki[:n]+"?"+mwiki[n+1:]

                                mwiki=mwiki.replace('amp;amp;', 'amp;') # Fix double-encoded entities
                                mwiki=mwiki.replace('amp;lt;','lt;')
                                mwiki=mwiki.replace('amp;gt;','gt;')
                                mwiki=mwiki.replace('amp;quot;','quot;')
                                mwiki=mwiki.replace('&amp;nbsp;','&#160;') # &nbsp not a valid XML entity
                                mwiki=mwiki.replace('%%%', '&lt;br/&gt;') # Replace Tiki line breaks
                                mwiki=mwiki.replace('&lt;/br&gt;', '') # attempt to replace br placeholders

                                # Replace entities in syntax highlighting
                                mwiki=mwiki.replace('lang=&amp;quot;', 'lang=&quot;')
                                mwiki=mwiki.replace('&amp;quot;&gt;', '&quot;&gt;')
                                mwiki=re.sub('(&lt;syntaxhighlight.*?)&quot;&gt;', '\\1&quot; enclose=&quot;div&quot;&gt;', mwiki) # Add enclose=div attributes, fixes formatting
                                mwiki=mwiki.replace('lang=&quot;sh&quot;', 'lang=&quot;bash&quot;')

                                while "  " in mwiki:
                                        mwiki=mwiki.replace("  ", " ")
                                mwiki=mwiki.replace('&lt;!--','<!--')
                                mwiki=mwiki.replace('--&gt;','-->')
                                mwiki=re.sub('--+>', '-->', mwiki)
                                mwiki=re.sub('<!--+', '<!--', mwiki)
                                mwiki=re.sub(r'^-{3}$', '----', mwiki, flags=re.MULTILINE) # Fix incorrect HR tags from Tiki

                                # the table of contents will have been seen as bold formatting
                                if len(headings)>=3:
                                        mwiki = mwiki.replace("'''TOC'''", '__TOC__')
                                        mwiki = mwiki.replace("'''NOTOC'''", '__NOTOC__')
                                else:
                                        mwiki = mwiki.replace("'''TOC'''\n\n", '')
                                        mwiki = mwiki.replace("'''NOTOC'''\n\n", '')
                                        mwiki = mwiki.replace("'''TOC'''\n", '')#if it's before bullets/numbers the second \n will have gone
                                        mwiki = mwiki.replace("'''NOTOC'''\n", '')

                                # Replace Tiki TOC's
                                mwiki=mwiki.replace('{maketoc}', '__TOC__')

                                # Tighten up extra newlines in table formatting
                                mwiki=mwiki.replace('{|\n\n', '{|\n') # Table starts
                                mwiki=mwiki.replace('\n\n|-\n\n', '\n|-\n') # Table rows
                                mwiki=mwiki.replace('\n\n|}', '\n|}') # Table ends

                                outputpage = unicode(outputpage, "utf-8")
                                outputpage+=mwiki+'</text>\n'
                                outputpage+='</revision>\n'
                                outputpage=outputpage.encode('utf-8')
                                totalSize+=len(outputpage)

                                #mediawiki has a maximum import file size so start a new file after that limit
                                if options.outputFile!='-':
                                        if totalSize > options.max*1024*1024:
                                                totalSize=len(unicode(outputpage, "Latin-1"))
                                                mwikixml.write('</page>')
                                                mwikixml.write('</mediawiki>')
                                                fileCount += 1
                                                mwikixml = open(outputFile[:-4]+str(fileCount)+outputFile[-4:], 'wb')
                                                sys.stderr.write('Creating new wiki xml file '+outputFile[:-4]+str(fileCount)+outputFile[-4:]+'\n')
                                                mwikixml.write('<mediawiki xml:lang="en">\n')
                                                #if this isn't the first part write page and title
                                                mwikixml.write('<page>\n')
                                                mwikixml.write('<title>'+title+'</title>')
                                        mwikixml.write(outputpage)
                                else:
                                        mwikixml.write(outputpage)
                        else:
                                if partcount != 1:
                                        if sys.stdout == False:
                                                sys.stderr.write(str(part.get_param('pagename'))+' version '+str(part.get_param('version'))+' wasn\'t counted')

                mwikixml.write('</page>')
                if uploads != []:
                        filepages[title] = uploads
                pagecount+=1
mwikixml.write('</mediawiki>')
sys.stderr.write('\nnumber of pages = '+str(pagecount)+' number of versions = '+str(versioncount)+'\n')
sys.stderr.write('with contributions by '+str(authors)+'\n')
sys.stderr.write('and file uploads on these pages: '+str(filepages.keys())+'\n')