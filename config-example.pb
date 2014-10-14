downloader: {
  storageFile: "d/http.kch"
  competitionsUrl: "http://www.kaggle.com/competitions/search?SearchVisibility=AllCompetitions&ShowActive=true&ShowCompleted=true&ShowProspect=true&ShowOpenToAll=true&ShowPrivate=true&ShowLimited=true"
}
sqliteSyncer: {
  sqliteFile: "d/kaggle.sqlite"
}
calendarSyncer: {
  authentication: {
    developersKey: "<developer-key>"
    serviceAccount: {
      email: "<service-account-email>"
      keysFile: "<service-account-pem>"
    }
  }
  targetAll: {
    email: "<email>@gmail.com"
    calendarId: "<calendar-id>@group.calendar.google.com"
  }
  targetInMoney: {
    email: "<email>@gmail.com"
    calendarId: "<calendar-id>@group.calendar.google.com"
  }
  targetKnowledge: {
    email: "<email>@gmail.com"
    calendarId: "<calendar-id>@group.calendar.google.com"
  }
}
