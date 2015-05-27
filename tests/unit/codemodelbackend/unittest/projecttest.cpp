﻿/****************************************************************************
**
** Copyright (C) 2015 Digia Plc and/or its subsidiary(-ies).
** Contact: http://www.qt-project.org/legal
**
** This file is part of Qt Creator.
**
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and Digia.  For licensing terms and
** conditions see http://www.qt.io/licensing.  For further information
** use the contact form at http://www.qt.io/contact-us.
**
** GNU Lesser General Public License Usage
** Alternatively, this file may be used under the terms of the GNU Lesser
** General Public License version 2.1 or version 3 as published by the Free
** Software Foundation and appearing in the file LICENSE.LGPLv21 and
** LICENSE.LGPLv3 included in the packaging of this file.  Please review the
** following information to ensure the GNU Lesser General Public License
** requirements will be met: https://www.gnu.org/licenses/lgpl.html and
** http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html.
**
** In addition, as a special exception, Digia gives you certain additional
** rights.  These rights are described in the Digia Qt LGPL Exception
** version 1.1, included in the file LGPL_EXCEPTION.txt in this package.
**
****************************************************************************/

#include "gtest/gtest.h"

#include "gmock/gmock-matchers.h"
#include "gmock/gmock-generated-matchers.h"
#include "gtest-qt-printing.h"

#include <projectpart.h>
#include <utf8stringvector.h>
#include <projects.h>
#include <projectpartsdonotexistexception.h>

#include <chrono>
#include <thread>

using testing::ElementsAre;
using testing::StrEq;
using testing::Pointwise;
using testing::Contains;
using testing::Gt;
using testing::Not;

namespace {

TEST(ProjectPart, CreateProjectPart)
{
    Utf8String projectPath(Utf8StringLiteral("/tmp/blah.pro"));

    CodeModelBackEnd::ProjectPart project(projectPath);

    ASSERT_THAT(project.projectPartId(), projectPath);
}

TEST(ProjectPart, CreateProjectPartWithProjectPartContainer)
{
    CodeModelBackEnd::ProjectPartContainer projectContainer(Utf8StringLiteral("pathToProjectPart.pro"), {Utf8StringLiteral("-O")});

    CodeModelBackEnd::ProjectPart project(projectContainer);

    ASSERT_THAT(project.projectPartId(), Utf8StringLiteral("pathToProjectPart.pro"));
    ASSERT_THAT(project.arguments(), Contains(StrEq("-O")));
}

TEST(ProjectPart, SetArguments)
{
    CodeModelBackEnd::ProjectPart project(Utf8StringLiteral("/tmp/blah.pro"));

    project.setArguments(Utf8StringVector({Utf8StringLiteral("-O"), Utf8StringLiteral("-fast")}));

    ASSERT_THAT(project.arguments(), ElementsAre(StrEq("-O"), StrEq("-fast")));
}

TEST(ProjectPart, ArgumentCount)
{
    CodeModelBackEnd::ProjectPart project(Utf8StringLiteral("/tmp/blah.pro"));

    project.setArguments(Utf8StringVector({Utf8StringLiteral("-O"), Utf8StringLiteral("-fast")}));

    ASSERT_THAT(project.argumentCount(), 2);
}

TEST(ProjectPart, TimeStampIsUpdatedAsArgumentChanged)
{
    CodeModelBackEnd::ProjectPart project(Utf8StringLiteral("/tmp/blah.pro"));
    auto lastChangeTimePoint = project.lastChangeTimePoint();
    std::this_thread::sleep_for(std::chrono::steady_clock::duration(1));

    project.setArguments(Utf8StringVector({Utf8StringLiteral("-O"), Utf8StringLiteral("-fast")}));

    ASSERT_THAT(project.lastChangeTimePoint(), Gt(lastChangeTimePoint));

}

TEST(ProjectPart, GetNonExistingPoject)
{
    CodeModelBackEnd::ProjectParts projects;

    ASSERT_THROW(projects.project(Utf8StringLiteral("pathToProjectPart.pro")), CodeModelBackEnd::ProjectPartDoNotExistException);
}

TEST(ProjectPart, AddProjectParts)
{
    CodeModelBackEnd::ProjectPartContainer projectContainer(Utf8StringLiteral("pathToProjectPart.pro"), {Utf8StringLiteral("-O")});
    CodeModelBackEnd::ProjectParts projects;

    projects.createOrUpdate({projectContainer});

    ASSERT_THAT(projects.project(projectContainer.projectPartId()), CodeModelBackEnd::ProjectPart(projectContainer));
    ASSERT_THAT(projects.project(projectContainer.projectPartId()).arguments(), ElementsAre(StrEq("-O")));
}

TEST(ProjectPart, UpdateProjectParts)
{
    CodeModelBackEnd::ProjectPartContainer projectContainer(Utf8StringLiteral("pathToProjectPart.pro"), {Utf8StringLiteral("-O")});
    CodeModelBackEnd::ProjectPartContainer projectContainerWithNewArguments(Utf8StringLiteral("pathToProjectPart.pro"), {Utf8StringLiteral("-fast")});
    CodeModelBackEnd::ProjectParts projects;
    projects.createOrUpdate({projectContainer});

    projects.createOrUpdate({projectContainerWithNewArguments});

    ASSERT_THAT(projects.project(projectContainer.projectPartId()), CodeModelBackEnd::ProjectPart(projectContainer));
    ASSERT_THAT(projects.project(projectContainer.projectPartId()).arguments(), ElementsAre(StrEq("-fast")));
}

TEST(ProjectPart, ThrowExceptionForAccesingRemovedProjectParts)
{
    CodeModelBackEnd::ProjectPartContainer projectContainer(Utf8StringLiteral("pathToProjectPart.pro"), {Utf8StringLiteral("-O")});
    CodeModelBackEnd::ProjectParts projects;
    projects.createOrUpdate({projectContainer});

    projects.remove({projectContainer.projectPartId()});

    ASSERT_THROW(projects.project(projectContainer.projectPartId()), CodeModelBackEnd::ProjectPartDoNotExistException);
}

TEST(ProjectPart, ProjectPartProjectPartIdIsEmptyfterRemoving)
{
    CodeModelBackEnd::ProjectPartContainer projectContainer(Utf8StringLiteral("pathToProjectPart.pro"), {Utf8StringLiteral("-O")});
    CodeModelBackEnd::ProjectParts projects;
    projects.createOrUpdate({projectContainer});
    CodeModelBackEnd::ProjectPart project(projects.project(projectContainer.projectPartId()));

    projects.remove({projectContainer.projectPartId()});

    ASSERT_TRUE(project.projectPartId().isEmpty());
}

TEST(Project, ThrowsForNotExistingProjectPartButRemovesAllExistingProject)
{
    CodeModelBackEnd::ProjectPartContainer projectContainer(Utf8StringLiteral("pathToProjectPart.pro"));
    CodeModelBackEnd::ProjectParts projects;
    projects.createOrUpdate({projectContainer});
    CodeModelBackEnd::ProjectPart project = *projects.findProjectPart(Utf8StringLiteral("pathToProjectPart.pro"));

    EXPECT_THROW(projects.remove({Utf8StringLiteral("doesnotexist.pro"), projectContainer.projectPartId()}),  CodeModelBackEnd::ProjectPartDoNotExistException);

    ASSERT_THAT(projects.projects(), Not(Contains(project)));
}

TEST(ProjectPart, HasProjectPart)
{
    CodeModelBackEnd::ProjectPartContainer projectContainer(Utf8StringLiteral("pathToProjectPart.pro"));
    CodeModelBackEnd::ProjectParts projects;
    projects.createOrUpdate({projectContainer});

    ASSERT_TRUE(projects.hasProjectPart(projectContainer.projectPartId()));
}

TEST(ProjectPart, DoNotHasProjectPart)
{
    CodeModelBackEnd::ProjectPartContainer projectContainer(Utf8StringLiteral("pathToProjectPart.pro"));
    CodeModelBackEnd::ProjectParts projects;
    projects.createOrUpdate({projectContainer});

    ASSERT_FALSE(projects.hasProjectPart(Utf8StringLiteral("doesnotexist.pro")));
}


}
