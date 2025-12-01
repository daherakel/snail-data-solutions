# IAM role policy attachments (existing policies)
resource "aws_iam_role_policy_attachment" "ahh_authorizer_role_bjvxzkht_awslambdabasicexecutionrole_e06395eb_6041_47e5_9226_f7b7ce2b7139" {
  role       = "AHH_Authorizer-role-bjvxzkht"
  policy_arn = "arn:aws:iam::471112687668:policy/service-role/AWSLambdaBasicExecutionRole-e06395eb-6041-47e5-9226-f7b7ce2b7139"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_generate_clinical_notes_role_2w9ey1r1_awslambdabasicexecutionrole_c8894a24_3b96_4f62_a80a_54704fb4fec7" {
  role       = "AHH_GENERATE_CLINICAL_NOTES-role-2w9ey1r1"
  policy_arn = "arn:aws:iam::471112687668:policy/service-role/AWSLambdaBasicExecutionRole-c8894a24-3b96-4f62-a80a-54704fb4fec7"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_generate_clinical_notes_role_2w9ey1r1_amazons3fullaccess" {
  role       = "AHH_GENERATE_CLINICAL_NOTES-role-2w9ey1r1"
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_generate_clinical_notes_role_2w9ey1r1_amazonbedrockfullaccess" {
  role       = "AHH_GENERATE_CLINICAL_NOTES-role-2w9ey1r1"
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_gettranscription_role_8tiisd9a_awslambdabasicexecutionrole_430c7f46_c96e_45ad_81d4_17f332d56f09" {
  role       = "AHH_GetTranscription-role-8tiisd9a"
  policy_arn = "arn:aws:iam::471112687668:policy/service-role/AWSLambdaBasicExecutionRole-430c7f46-c96e-45ad-81d4-17f332d56f09"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_gettranscription_role_8tiisd9a_amazontranscribefullaccess" {
  role       = "AHH_GetTranscription-role-8tiisd9a"
  policy_arn = "arn:aws:iam::aws:policy/AmazonTranscribeFullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_processaudio_role_fv8sqvna_awslambdabasicexecutionrole_28d3fd7b_17f6_47dc_9c9b_ee7081522ea3" {
  role       = "AHH_ProcessAudio-role-fv8sqvna"
  policy_arn = "arn:aws:iam::471112687668:policy/service-role/AWSLambdaBasicExecutionRole-28d3fd7b-17f6-47dc-9c9b-ee7081522ea3"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_processaudio_role_fv8sqvna_amazontranscribefullaccess" {
  role       = "AHH_ProcessAudio-role-fv8sqvna"
  policy_arn = "arn:aws:iam::aws:policy/AmazonTranscribeFullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_processaudio_role_fv8sqvna_comprehendfullaccess" {
  role       = "AHH_ProcessAudio-role-fv8sqvna"
  policy_arn = "arn:aws:iam::aws:policy/ComprehendFullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_processaudio_role_fv8sqvna_comprehendreadonly" {
  role       = "AHH_ProcessAudio-role-fv8sqvna"
  policy_arn = "arn:aws:iam::aws:policy/ComprehendReadOnly"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_processaudio_role_fv8sqvna_comprehenddataaccessrolepolicy" {
  role       = "AHH_ProcessAudio-role-fv8sqvna"
  policy_arn = "arn:aws:iam::aws:policy/service-role/ComprehendDataAccessRolePolicy"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_processaudio_role_fv8sqvna_comprehendmedicalfullaccess" {
  role       = "AHH_ProcessAudio-role-fv8sqvna"
  policy_arn = "arn:aws:iam::aws:policy/ComprehendMedicalFullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_processaudio_role_fv8sqvna_amazons3fullaccess" {
  role       = "AHH_ProcessAudio-role-fv8sqvna"
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_helloworld_role_rrabedl8_awslambdabasicexecutionrole_ad003b1f_f67a_4579_bb2c_65743a35d90e" {
  role       = "AHH_helloworld-role-rrabedl8"
  policy_arn = "arn:aws:iam::471112687668:policy/service-role/AWSLambdaBasicExecutionRole-ad003b1f-f67a-4579-bb2c-65743a35d90e"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_helloworld_role_rrabedl8_amazontranscribefullaccess" {
  role       = "AHH_helloworld-role-rrabedl8"
  policy_arn = "arn:aws:iam::aws:policy/AmazonTranscribeFullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_helloworld_role_rrabedl8_translatefullaccess" {
  role       = "AHH_helloworld-role-rrabedl8"
  policy_arn = "arn:aws:iam::aws:policy/TranslateFullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_helloworld_role_rrabedl8_comprehendmedicalfullaccess" {
  role       = "AHH_helloworld-role-rrabedl8"
  policy_arn = "arn:aws:iam::aws:policy/ComprehendMedicalFullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_helloworld_role_rrabedl8_amazons3fullaccess" {
  role       = "AHH_helloworld-role-rrabedl8"
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ahh_helloworld_role_rrabedl8_awslambda_fullaccess" {
  role       = "AHH_helloworld-role-rrabedl8"
  policy_arn = "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
  lifecycle { prevent_destroy = true }
}

resource "aws_iam_role_policy_attachment" "ibold_price_detector_role_8h6atqmq_awslambdabasicexecutionrole_c021688d_9af8_4902_b0ff_c152df0816e7" {
  role       = "ibold-price-detector-role-8h6atqmq"
  policy_arn = "arn:aws:iam::471112687668:policy/service-role/AWSLambdaBasicExecutionRole-c021688d-9af8-4902-b0ff-c152df0816e7"
  lifecycle { prevent_destroy = true }
}
