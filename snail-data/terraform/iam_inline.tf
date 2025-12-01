# IAM inline role policies
resource "aws_iam_role_policy" "ahh_authorizer_role_bjvxzkht_secretroleapi" {
  name = "SecretRoleAPI"
  role = "AHH_Authorizer-role-bjvxzkht"
  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : "secretsmanager:GetSecretValue",
          "Resource" : "*"
        }
      ]
    }
  )
  lifecycle { prevent_destroy = true }
}
