Select Distinct ScriptProjects.Id, ScriptVersions.Id, Scripts.AuthorUserId, Users.DisplayName, Competitions.Id, Competitions.CompetitionName, ScriptVersions.Title, ScriptVersions.ScriptContent
From ScriptVersions
INNER JOIN Scripts
ON ScriptVersions.ScriptId = Scripts.Id
INNER JOIN ScriptProjects
ON Scripts.ScriptProjectId = ScriptProjects.Id
INNER JOIN Competitions
ON ScriptProjects.CompetitionId = Competitions.Id
INNER JOIN Users
ON Scripts.AuthorUserId = Users.Id
WHERE ScriptVersions.ScriptLanguageId = 2
